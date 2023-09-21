
from app.utils.openai_utils import chat_text_call
from flask import render_template, request, jsonify, redirect, url_for, Response
from flask_login import login_required, current_user, logout_user
from app import login_manager, db
from app.utils.file.file_utils import *
from app.utils.message_utils import *
from app.utils.manager_utils import *
from flask import Blueprint

main = Blueprint('main', __name__)


@main.route('/', methods=["GET", "POST"])
@login_required
def home():
    session["ID_USER"] = current_user.id
    session.setdefault('MODEL_API_OPTION_CHOOSE', 'gpt-3.5-turbo')
    session.setdefault('LANGUAGE_OPTION_CHOOSE', 'English')
    session.modified = True

    session['ELEMENTS_TRANSLATE'] = []
    session['ELEMENTS_AUDIO'] = []
    session['ELEMENTS_CHAT'] = []
    session['FILE_CONTEXT'] = []
    session['CONTEXT'] = [{'role': "system", 'content': "Sei un assistente, hai il compito di rispondere alle mie "
                                                        "domande,"
                                                        "eseguire i miei ordini e di aprire i link che ti mando."}]
    session.modified = True

    if 'INFORMATION' not in session:
        session['INFORMATION'] = {"Num_Message": 0, "Num_Token": 0}
    session.modified = True

    if current_user.user_elements_chat is None:
        current_user.user_elements_chat = []
    if current_user.user_elements_translate is None:
        current_user.user_elements_translate = []
    if current_user.user_elements_audio is None:
        current_user.user_elements_audio = []
    if current_user.user_file_in_context is None:
        current_user.user_file_in_context = []
    if current_user.user_context is None:
        current_user.user_context = [{'role': "system", 'content': "Sei un assistente, hai il compito di rispondere "
                                                                   "alle mie domande, eseguire i miei ordini e di "
                                                                   "aprire i link che ti mando."}]

    db.session.commit()

    if len(current_user.user_elements_chat) > 0 or len(current_user.user_file_in_context) > 0:
        return render_template('index.html', elements=current_user.user_elements_chat, file_context=current_user.user_file_in_context,
                               information=session['INFORMATION'], user=current_user.username,
                               user_id=session["ID_USER"], lang=session['LANGUAGE_OPTION_CHOOSE'])

    return render_template('index.html', information=session['INFORMATION'], user=current_user.username,
                           user_id=session["ID_USER"], lang=session['LANGUAGE_OPTION_CHOOSE'])


@main.route('/get_elements', methods=["GET", "POST"])
@login_required
def get_elements():
    try:
        elements = request.form.get('sidebar')

        elements_map = {
            'chat_sidebar': 'user_elements_chat',
            'audio_sidebar': 'user_elements_audio',
            'translate_sidebar': 'user_elements_translate'
        }

        data = {
            'section': elements,
            'file': current_user.user_file_in_context,
            'information': session.get('INFORMATION', None)
        }

        if elements in elements_map:
            data['elements'] = getattr(current_user, elements_map[elements], None)
        return jsonify(data)
    except Exception as e:
        print(f"Errore : {str(e)}")
        return jsonify({"error": "Errore nel caricamento della chat.\nChat non Aggiornata.\n" + str(e)}), 500


@main.route('/process_form', methods=["GET", "POST"])
@login_required
def text_form_response():
    if current_user and current_user.has_chat_request_in_progress:
        return jsonify(
            {"error": "Un'altra richiesta è in corso per questo utente.", "request_in_progress": True}), 400

    current_user.has_chat_request_in_progress = True
    db.session.commit()

    try:

        text = request.form.get('text')
        escaped_text = escape(text)

        translate = request.form.get('translate')

        data = {
            'file': current_user.user_file_in_context,
            'information': session['INFORMATION']
        }

        if translate == "true":
            try:
                response = translate_manager(text, session['LANGUAGE_OPTION_CHOOSE'], 'text')
            except Exception as e:
                response = f"Errore nella richiesta\n{str(e)}"
            current_user.user_elements_translate.append({'response_text': decode(response)})
            db.session.commit()

            data['elements'] = current_user.user_elements_translate
            data['section'] = 'translate_sidebar'
        else:
            try:
                response = chat_text_call(text)
            except Exception as e:
                response = f"Errore nella richiesta\n{str(e)}"
            current_user.user_elements_chat.append({'user_text': escaped_text, 'response_text': decode(response)})
            db.session.commit()

            data['elements'] = current_user.user_elements_chat
            data['section'] = 'chat_sidebar'

        return jsonify(data)
    except Exception as e:
        print(f"Errore generico nella text form response: {str(e)}")
        return jsonify({"error": "Errore generico nella text response" + str(e)}), 500
    finally:
        current_user.has_chat_request_in_progress = False
        db.session.commit()


@main.route('/upload_file', methods=['POST'])
@login_required
def upload_file():
    if current_user and current_user.has_chat_request_in_progress:
        return jsonify(
            {"error": "Un'altra richiesta è in corso per questo utente.", "request_in_progress": True}), 400

    current_user.has_chat_request_in_progress = True
    db.session.commit()

    try:
        uploaded_files = request.files.getlist('file[]')
        for file in uploaded_files:
            if file.filename != '' and file:
                file_manager(file, "chat")

        data = {
            'section': "chat_sidebar",
            'elements': current_user.user_elements_chat,
            'file': current_user.user_file_in_context,
            'information': session["INFORMATION"]
        }

        db.session.commit()
        return jsonify(data)
    except Exception as e:
        print(f"Errore durante l'estrazione del contenuto del file: {str(e)}")
        return jsonify({"error": "File corrotto o non utilizzabile.\n" + str(e)}), 500
    finally:
        current_user.has_chat_request_in_progress = False
        db.session.commit()


@main.route('/model_chat_api', methods=['POST'])
@login_required
def change_chat_model():
    session['MODEL_API_OPTION_CHOOSE'] = request.form.get('new_value')
    return jsonify({"Message": "Modello Cambiato"})


@main.route('/clear_elements', methods=['POST'])
@login_required
def clear_elements():
    try:
        elements = request.form.get('sidebar')

        elements_map = {
            'chat_sidebar': 'user_elements_chat',
            'audio_sidebar': 'user_elements_audio',
            'translate_sidebar': 'user_elements_translate'
        }
        elements_map_folder = {
            'audio_sidebar': 'audio_folder',
            'translate_sidebar': 'translate_folder',
        }

        if elements in elements_map:
            setattr(current_user, elements_map[elements], [])
            db.session.commit()

        try:
            if elements in elements_map_folder:
                clear_file_folder(folder_path(elements_map_folder[elements]))
            return jsonify({"Message": "Elements Puliti"})
        except Exception as e:
            print(f"Errore nella eliminazione dei file: {str(e)}")
            return jsonify({"error": "Errore nella eliminazione dei file:\n" + str(e)}), 500
    except Exception as e:
        print(f"Errore nella pulizia della chat: {str(e)}")
        return jsonify({"error": "Errore nella pulizia della chat:\n" + str(e)}), 500


@main.route('/clear_context', methods=['POST'])
@login_required
def clear_context():
    try:
        file_path = "log/" + str(session["ID_USER"]) + "/log.json"
        log_context_to_file(file_path, current_user.user_context)
        current_user.user_elements_chat = []
        current_user.user_file_in_context = []
        current_user.user_context = []
        current_user.user_context.append({'role': "system", 'content': "You are an assistant"})

        db.session.commit()
        session['INFORMATION'].clear()
        session['INFORMATION'] = {"Num_Message": 0, "Num_Token": 0}
        session.modified = True

        return jsonify({"Message": "Elements Puliti"})
    except Exception as e:
        print(f"Errore : {str(e)}")
        return jsonify({"error": "Errore nella pulizia del contexto"}), 500


@main.route('/remove_file', methods=['POST'])
@login_required
def remove_file():
    try:
        new_context = []
        new_file_context = []

        for file in current_user.user_file_in_context:
            if request.form.get('file') not in file["file"]:
                new_file_context.append(file)

        current_user.user_file_in_context = new_file_context

        for cont in current_user.user_context:
            if request.form.get('file') not in cont["content"]:
                new_context.append(cont)

        current_user.user_context = new_context
        current_user.user_elements_chat.append(
            {'response_text': "<p class='w-100 text-center my-auto'> " + request.form.get(
                'file') + " <span class='fs-6 fw-bold'>rimosso</span> dal contexto della Chat.</p>",
             'file_context': request.form.get('file')})

        db.session.commit()
        data = {
            "section": "chat_sidebar",
            'elements': current_user.user_elements_chat,
            'file': current_user.user_file_in_context,
            'information': session["INFORMATION"]
        }

        return jsonify(data)
    except Exception as e:
        print(f"Errore : {str(e)}")
        return jsonify({"error": "Errore nella pulizia del contexto"}), 500


@main.route('/get_token', methods=['POST'])
@login_required
def get_token():
    try:
        return jsonify(
            {"token": num_tokens_from_messages(request.form.get('text', session["MODEL_API_OPTION_CHOOSE"]))})
    except Exception as e:
        print(f"Errore : {str(e)}")
        return jsonify({"error": "Errore nel calcolo dei token"}), 500


@main.route("/LogOut", methods=['POST'])
def logOut_route():
    try:
        logout_user()
        session.clear()

        return jsonify({"status": "success", "message": "Logged out successfully"}), 200
    except Exception as e:
        print(f"Errore : {str(e)}")
        return jsonify({"error": "Errore durante il logOut"}), 500


# ===============================================
# TRANSLATE


@main.route('/language_select', methods=['POST'])
@login_required
def change_lang():
    session['LANGUAGE_OPTION_CHOOSE'] = request.form.get('new_value')

    print(session['LANGUAGE_OPTION_CHOOSE'])
    return jsonify({"Message": "Modello Cambiato"})


@main.route("/translate_file", methods=['POST'])
def translate_file_response():
    if current_user and current_user.has_chat_request_in_progress:
        return jsonify(
            {"error": "Un'altra richiesta è in corso per questo utente.", "request_in_progress": True}), 400

    current_user.has_chat_request_in_progress = True
    db.session.commit()
    send_sse_message("bar", "Elaborazione File", 30, "trans")
    try:
        file = request.files['file']
        file_manager(file, "translate", request.form.get('opt'))
        db.session.commit()

        data = {
            'section': "translate_sidebar",
            'elements': current_user.user_elements_translate,
            'file': current_user.user_file_in_context,
            'information': session["INFORMATION"]
        }

        db.session.commit()

        return jsonify(data)
    except Exception as e:
        print(f"Errore : {str(e)}")
        return jsonify({"error": f"Errore durante la traduzione dei file\n{str(e)}"}), 500
    finally:
        current_user.has_chat_request_in_progress = False
        db.session.commit()


# ===============================================
# Audio

@main.route("/transcribe_audio", methods=['POST'])
def transcribe_audio_response():
    if current_user and current_user.has_audio_request_in_progress:
        return jsonify(
            {"error": "Un'altra richiesta è in corso per questo utente.", "request_in_progress": True}), 400

    current_user.has_audio_request_in_progress = True
    db.session.commit()
    
    try:
        file = request.files['file']

        file_manager(file, 'audio', request.form.get('transcriptionOption'),
                     request.form.get('translationLanguage'))
        db.session.commit()

        data = {
            'section': "audio_sidebar",
            'elements': current_user.user_elements_audio,
            'file': current_user.user_file_in_context,
            'information': session["INFORMATION"]
        }


        return jsonify(data)
    except Exception as e:
        print(f"Errore : {str(e)}")
        return jsonify({"error": "Errore durante la trascrizione dei file"}), 500
    finally:
        current_user.has_audio_request_in_progress = False
        db.session.commit()


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("auth.login"))
