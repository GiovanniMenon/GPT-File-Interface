
from app.utils.openai_utils import chat_text_call
from flask import render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user, logout_user
from app import login_manager, db
from app.utils.file.file_utils import *
from app.utils.message_utils import *
from app.utils.manager_utils import *
from flask import Blueprint

import threading
import time

main = Blueprint('main', __name__)
user_locks = {}
user_audio_locks = {}


def updateDb():
    current_user.elements_chat = session['ELEMENTS_CHAT']
    current_user.elements_translate = session['ELEMENTS_TRANSLATE']
    current_user.elements_audio = session['ELEMENTS_AUDIO']

    current_user.file_context = session['FILE_CONTEXT']
    current_user.context = session['CONTEXT']
    db.session.commit()


def updateSession():
    session['ELEMENTS_CHAT'] = current_user.elements_chat
    session['ELEMENTS_TRANSLATE'] = current_user.elements_translate
    session['ELEMENTS_AUDIO'] = current_user.elements_audio

    session['FILE_CONTEXT'] = current_user.file_context
    session['CONTEXT'] = current_user.context


@main.route('/', methods=["GET", "POST"])
@login_required
def home():
    session["ID_USER"] = current_user.id
    session.modified = True
    session.setdefault('MODEL_API_OPTION_CHOOSE', 'gpt-3.5-turbo')
    session.setdefault('LANGUAGE_OPTION_CHOOSE', 'Inglese')

    if 'INFORMATION' not in session:
        session['INFORMATION'] = {"Num_Message": 0, "Num_Token": 0}
        session.modified = True

    if current_user.elements_audio:
        session['ELEMENTS_AUDIO'] = current_user.elements_audio
    else:
        session['ELEMENTS_AUDIO'] = []
    session.modified = True
    if current_user.elements_translate:
        session['ELEMENTS_TRANSLATE'] = current_user.elements_translate
    else:
        session['ELEMENTS_TRANSLATE'] = []
    session.modified = True
    if current_user.elements_chat:
        session['ELEMENTS_CHAT'] = current_user.elements_chat
    else:
        session['ELEMENTS_CHAT'] = []
    session.modified = True
    if current_user.file_context:
        session['FILE_CONTEXT'] = current_user.file_context
    else:
        session['FILE_CONTEXT'] = []
    session.modified = True
    if current_user.context:
        session['CONTEXT'] = current_user.context
    else:
        session['CONTEXT'] = [{'role': "system", 'content': "Sei un assistente, hai il compito di rispondere alle mie "
                                                            "domande,"
                                                            "eseguire i miei ordini e di aprire i link che ti mando."}]
    session.modified = True
    if len(session['ELEMENTS_CHAT']) > 0 or len(session['FILE_CONTEXT']) > 0:
        return render_template('index.html', elements=session['ELEMENTS_CHAT'], file_context=session['FILE_CONTEXT'],
                               information=session['INFORMATION'], user=current_user.username,
                               lang=session['LANGUAGE_OPTION_CHOOSE'])

    return render_template('index.html', information=session['INFORMATION'], user=current_user.username,
                           lang=session['LANGUAGE_OPTION_CHOOSE'])


@main.route('/get_elements', methods=["GET", "POST"])
@login_required
def get_elements():
    try:
        elements = request.form.get('sidebar')
        updateSession()

        elements_map = {
            'chat_sidebar': 'ELEMENTS_CHAT',
            'audio_sidebar': 'ELEMENTS_AUDIO',
            'translate_sidebar': 'ELEMENTS_TRANSLATE'
        }

        data = {
            'section': elements,
            'file': session.get('FILE_CONTEXT', None),
            'information': session.get('INFORMATION', None)
        }

        # Imposta 'elements' nel dizionario 'data' se esiste una corrispondenza
        if elements in elements_map:
            data['elements'] = session.get(elements_map[elements], None)

        return jsonify(data)
    except Exception as e:
        print(f"Errore : {str(e)}")
        return jsonify({"error": "Errore nel caricamento della chat.\nChat non Aggiornata.\n" + str(e)}), 500


@main.route('/process_form', methods=["GET", "POST"])
@login_required
def text_form_response():
    user_id = session["ID_USER"]

    if user_id not in user_locks:
        user_locks[user_id] = threading.Lock()

    if user_locks[user_id].locked():
        return jsonify({"message": "Un'altra richiesta è in corso per questo utente."}), 400

    with user_locks.setdefault(user_id, threading.Lock()):
        try:
            text = request.form.get('text')
            escaped_text = escape(text)

            translate = request.form.get('translate')

            data = {
                'file': session['FILE_CONTEXT'],
                'information': session['INFORMATION']
            }

            if translate == "true":
                response = translate_manager(text, session['LANGUAGE_OPTION_CHOOSE'])
                session['ELEMENTS_TRANSLATE'].append({'response_text': decode(response)})
                session.modified = True
                data['elements'] = session['ELEMENTS_TRANSLATE']
                data['section'] = 'translate_sidebar'

            else:
                response = chat_text_call(text)
                session['ELEMENTS_CHAT'].append({'user_text': escaped_text, 'response_text': decode(response)})

                data['elements'] = session['ELEMENTS_CHAT']
                data['section'] = 'chat_sidebar'

            updateDb()
            return jsonify(data)
        finally:
            # Rimuovi il blocco dell'utente quando la richiesta è completata
            user_locks.pop(user_id, None)


@main.route('/upload_file', methods=['POST'])
@login_required
def upload_file():
    user_id = session["ID_USER"]

    if user_id not in user_locks:
        user_locks[user_id] = threading.Lock()

    if user_locks[user_id].locked():
        return jsonify({"message": "Un'altra richiesta è in corso per questo utente."}), 400
    with user_locks.setdefault(user_id, threading.Lock()):
        try:
            try:
                uploaded_files = request.files.getlist('file[]')
                for file in uploaded_files:
                    if file.filename != '' and file:
                        file_manager(file, "chat")
                        updateDb()
                data = {
                    'section': "chat_sidebar",
                    'elements': session['ELEMENTS_CHAT'],
                    'file': session['FILE_CONTEXT'],
                    'information': session["INFORMATION"]
                }

                return jsonify(data)
            except Exception as e:
                print(f"Errore durante l'estrazione del contenuto del file: {str(e)}")
                return jsonify({"error": "Errore nel caricamento del file.\nFile non caricato.\n" + str(e)}), 500
        finally:
            # Rimuovi il blocco dell'utente quando la richiesta è completata
            user_locks.pop(user_id, None)


@main.route('/model_api', methods=['POST'])
@login_required
def change_model():
    session['MODEL_API_OPTION_CHOOSE'] = request.form.get('new_value')
    return jsonify({"Message": "Modello Cambiato"})


@main.route('/clear_elements', methods=['POST'])
@login_required
def clear_elements():
    try:
        elements = request.form.get('sidebar')

        elements_map = {
            'chat_sidebar': 'ELEMENTS_CHAT',
            'audio_sidebar': 'ELEMENTS_AUDIO',
            'translate_sidebar': 'ELEMENTS_TRANSLATE'
        }
        elements_map_folder = {
            'audio_sidebar': 'audio_folder',
            'translate_sidebar': 'translate_folder',
        }
        if elements in elements_map:
            session[elements_map[elements]].clear()

        session.modified = True
        updateDb()
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

        file_path = "history/" + str(session["ID_USER"]) + "/log.json"
        log_context_to_file(file_path, session['CONTEXT'])
        session['ELEMENTS_CHAT'].clear()
        session.modified = True
        session['CONTEXT'].clear()

        session.modified = True
        session['INFORMATION'].clear()

        session['INFORMATION'] = {"Num_Message": 0, "Num_Token": 0}
        session.modified = True

        session['CONTEXT'].append({'role': "system", 'content': "You are an assistant"})
        session.modified = True
        session['FILE_CONTEXT'].clear()
        session.modified = True

        updateDb()

        return jsonify({"Message": "Elements Puliti"})
    except Exception as e:
        print(f"Errore : {str(e)}")
        return jsonify({"error": "Errore nella pulizia del contexto"}), 500


@main.route('/remove_file', methods=['POST'])
@login_required
def remove_file():
    user_id = session["ID_USER"]

    if user_id not in user_locks:
        user_locks[user_id] = threading.Lock()

    if user_locks[user_id].locked():
        return jsonify({"message": "Un'altra richiesta è in corso per questo utente."}), 400
    with user_locks.setdefault(user_id, threading.Lock()):
        try:
            try:
                new_context = []
                new_file_context = []

                for file in session['FILE_CONTEXT']:
                    if request.form.get('file') not in file["file"]:
                        new_file_context.append(file)

                session['FILE_CONTEXT'] = new_file_context
                session.modified = True

                for cont in session['CONTEXT']:
                    if request.form.get('file') not in cont["content"]:
                        new_context.append(cont)

                session['CONTEXT'] = new_context
                session['ELEMENTS_CHAT'].append(
                    {'response_text': "<p class='w-100 text-center my-auto'> " + request.form.get(
                        'file') + " <span class='fs-6 fw-bold'>rimosso</span> dal contexto della Chat.</p>",
                     'file_context': request.form.get('file')})
                session.modified = True
                data = {
                    "section": "chat_sidebar",
                    'elements': session['ELEMENTS_CHAT'],
                    'file': session['FILE_CONTEXT'],
                    'information': session["INFORMATION"]
                }

                updateDb()
                return jsonify(data)
            except Exception as e:
                print(f"Errore : {str(e)}")
                return jsonify({"error": "Errore nella pulizia del contexto"}), 500
        finally:
            # Rimuovi il blocco dell'utente quando la richiesta è completata
            user_locks.pop(user_id, None)


@main.route('/get_token', methods=['POST'])
@login_required
def get_token():
    try:
        return jsonify({"token": num_tokens_from_messages(request.form.get('text', session["MODEL_API_OPTION_CHOOSE"]))})
    except Exception as e:
        print(f"Errore : {str(e)}")
        return jsonify({"error": "Errore nel calcolo dei token"}), 500


@main.route("/LogOut", methods=['POST'])
def logOut_route():
    try:
        updateDb()
        logout_user()
        session.clear()
        session.modified = True
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
    session.modified = True
    print(session['LANGUAGE_OPTION_CHOOSE'])
    return jsonify({"Message": "Modello Cambiato"})


@main.route("/translate_file", methods=['POST'])
def translate_file_response():
    user_id = session["ID_USER"]

    if user_id not in user_locks:
        user_locks[user_id] = threading.Lock()

    if user_locks[user_id].locked():
        return jsonify({"message": "Un'altra richiesta è in corso per questo utente."}), 400
    with user_locks.setdefault(user_id, threading.Lock()):
        try:
            try:
                file = request.files['file']
                file_manager(file, "translate", "")

                data = {
                    'section': "translate_sidebar",
                    'elements': session['ELEMENTS_TRANSLATE'],
                    'file': session['FILE_CONTEXT'],
                    'information': session["INFORMATION"]
                }
                current_user.elements_translate = session['ELEMENTS_TRANSLATE']
                db.session.commit()

                updateDb()
                return jsonify(data)
            except Exception as e:
                print(f"Errore : {str(e)}")
                return jsonify({"error": "Errore durante la traduzione dei file"}), 500
        finally:
            # Rimuovi il blocco dell'utente quando la richiesta è completata
            user_locks.pop(user_id, None)


# ===============================================
# Audio

@main.route("/transcribe_audio", methods=['POST'])
def transcribe_audio_response():
    user_id = session["ID_USER"]

    if user_id not in user_audio_locks:
        user_audio_locks[user_id] = threading.Lock()

    if user_audio_locks[user_id].locked():
        return jsonify({"message": "Un'altra richiesta è in corso per questo utente."}), 400
    with user_audio_locks.setdefault(user_id, threading.Lock()):
        try:
            try:
                file = request.files['file']

                file_manager(file, 'audio', request.form.get('transcriptionOption'), request.form.get('translationLanguage'))

                data = {
                    'section': "audio_sidebar",
                    'elements': session['ELEMENTS_AUDIO'],
                    'file': session['FILE_CONTEXT'],
                    'information': session["INFORMATION"]
                }
                current_user.elements_audio = session['ELEMENTS_AUDIO']
                db.session.commit()
                return jsonify(data)
            except Exception as e:
                print(f"Errore : {str(e)}")
                return jsonify({"error": "Errore durante la trascrizione dei file"}), 500
        finally:
            # Rimuovi il blocco dell'utente quando la richiesta è completata
            user_audio_locks.pop(user_id, None)


# ===============================================
# Cluster

@main.route("/embedded_file", methods=['POST'])
def embedded_file_response():
    file = request.files['file']

    file_manager(file, "embedded")

    data = {
        'elements': session['ELEMENTS_CHAT'],
        'file': session['FILE_CONTEXT'],
        'information': session["INFORMATION"]
    }
    updateDb()
    return jsonify(data)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("auth.login"))
