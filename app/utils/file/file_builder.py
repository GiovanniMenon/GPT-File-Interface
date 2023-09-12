
from app.utils.file.file_utils import write_file
from app.utils.message_utils import num_tokens_from_messages, split_text_into_sections
from app.utils.openai_utils import audio_text_call, translate_text_with_gpt
import concurrent.futures
import functools


def file_chat_builder(text, filename):
    from flask import session
    session['FILE_CONTEXT'].append({"file": filename, "token": num_tokens_from_messages(text)})

    session['CONTEXT'].append(
        {"role": "system", "content": "Aggiungi il seguente contenuto al contesto con il nome " + filename})
    session['CONTEXT'].append({'role': "user", 'content': "file-name : " + filename + ", content : " + text})

    session['ELEMENTS_CHAT'].append({'response_text': "<span class='fs-6 fw-bold'><b>OPERAZIONE : </b> </span>",
                                     'file_context': filename,
                                     'link_text': "<a class='' id='cont_ai_chat_file' \
                                     style='display:block;' > <pre> <span class='mx-auto'>" + filename +
                                     "<b> aggiunto</b> al contesto della Chat. </span> <i class='fa-solid "
                                     "fa-file'></i></pre> </a>"})


def file_translate_builder(text):
    from flask import session
    from app.utils.manager_utils import translate_manager

    text = translate_manager(text, session['LANGUAGE_OPTION_CHOOSE'], session['MODEL_TRANS_MODEL'])
    path_trascription = write_file(text, "translate_folder")

    words = text.split()
    if len(words) > 100:
        result_print = " ".join(words[:100])
        result_print += " ...."
    else:
        result_print = text
    session['ELEMENTS_TRANSLATE'].append({'response_text': result_print,
                                          'link_text': "<a href='" + path_trascription + "' id='cont_ai_chat_file' \
                                    style='display:block;' download> <pre> Scarica il File : " +
                                                       " <i class='fa-solid fa-file'></i></pre> </a>"})


def file_audio_builder(text, audio_opt, audio_lang):

    from flask import session
    from app.utils.manager_utils import translate_manager
    try:
        if num_tokens_from_messages(text) >= 15500:
            raise Exception("La trascrizione supera il limite di Token. TOKEN : " + str(num_tokens_from_messages(text)))

        if audio_opt == 'Trascrizione':
            result = text
        elif audio_opt == 'Traduzione':
            result = translate_manager(text, audio_lang)
        else:
            result = audio_text_call(audio_opt, text)

        words = result.split()
        result_print = " ".join(words[:100]) + " ...." if len(words) > 100 else result

        if audio_opt == 'Trascrizione':
            path_trascription = write_file(result, "audio_folder")
            session['ELEMENTS_AUDIO'].append({'response_text': result_print,
                                              'link_text': "<a href='" + path_trascription + "' id='cont_ai_chat_file' \
                                               style='display:block;' download> <pre> Scarica la Trascrizione : " +
                                                           " <i class='fa-solid fa-file'></i></pre> </a>"})
        else:
            path_trascription_opt = write_file(result, "audio_folder")
            path_trascription = write_file(text, "audio_folder")
            session['ELEMENTS_AUDIO'].append(
                {'response_text': result_print,
                 'link_text': "<a href='" + path_trascription_opt + "' ""id='cont_ai_chat_file' \
                  style='display:block;' download> <pre> Scarica il file : " \
                  " <i class='fa-solid fa-file'></i></pre>" 
                  "<a href='" + path_trascription + "' id='cont_ai_chat_file' \
                  style='display:block ;' class='mt-2' download> <pre> Scarica la Trascrizione : " +
                  " <i class='fa-solid fa-file'></i></pre> </a>"})
    except Exception as e:

        if audio_opt == 'Trascrizione':
            words = text.split()
            result_print = " ".join(words[:100]) + " ...." if len(words) > 100 else text
            path_trascription = write_file(text, "audio_folder")
            session['ELEMENTS_AUDIO'].append({'response_text': result_print,
                                              'link_text': "<a href='" + path_trascription + "' id='cont_ai_chat_file' \
                                               style='display:block;' download> <pre> Scarica la Trascrizione : " +
                                                           " <i class='fa-solid fa-file'></i></pre> </a>"})
        else:

            result = ""
            if audio_opt == 'Traduzione':
                segments = split_text_into_sections(text, 3500)
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    translate_call_with_lang = functools.partial(translate_text_with_gpt, audio_lang)
                    results = executor.map(translate_call_with_lang, segments)
                    result = ''.join(results)

            else:
                segments = split_text_into_sections(text, 13000)
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    translate_call_with_lang = functools.partial(audio_text_call, audio_opt)
                    results = executor.map(audio_text_call, segments)
                    result = ''.join(results)

            words = result.split()
            result_print = " ".join(words[:100]) + " ...." if len(words) > 100 else result

            path_trascription_opt = write_file(result, "audio_folder")
            path_trascription = write_file(text, "audio_folder")
            session['ELEMENTS_AUDIO'].append(
                {'response_text': result_print,
                 'link_text': "<a href='" + path_trascription_opt + "' ""id='cont_ai_chat_file' \
                             style='display:block;' download> <pre> Scarica il file : " \
                                                                    " <i class='fa-solid fa-file'></i></pre>"
                                                                    "<a href='" + path_trascription + "' id='cont_ai_chat_file' \
                             style='display:block ;' class='mt-2' download> <pre> Scarica la Trascrizione : " +
                              " <i class='fa-solid fa-file'></i></pre> </a>"})
