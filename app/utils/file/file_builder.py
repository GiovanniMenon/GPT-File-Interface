from app.utils.file.file_utils import write_file
from app.utils.message_utils import num_tokens_from_messages, split_text_into_sections, send_sse_message
from app.utils.openai_utils import audio_text_call, translate_file_text_with_gpt
import concurrent.futures
import functools


def file_chat_builder(text, filename):
    # Dato un testo lo aggiunge al contesto crea la risposta grafica

    from flask_login import current_user
    current_user.user_file_in_context.append({"file": filename, "token": num_tokens_from_messages(text)})

    current_user.user_context.append(
        {"role": "system", "content": "Aggiungi il seguente contenuto al contesto con il nome " + filename})
    current_user.user_context.append({'role': "user", 'content': "file-name : " + filename + ", content : " + text})

    current_user.user_elements_chat.append({'response_text': "<span class='fs-6 fw-bold'><b>OPERAZIONE : </b> </span>",
                                            'file_context': filename,
                                            'link_text': "<a class='' id='cont_ai_chat_file' \
                                            style='display:block;' > <pre> <span class='mx-auto'>" + filename +
                                                         "<b> aggiunto</b> al contesto della Chat. </span> <i "
                                                         "class='fa-solid"
                                                         "fa-file'></i></pre> </a>"})


def file_translate_builder(text, filename):
    # Dato un testo lo traduce e crea la risposta grafica
    from flask import session
    from flask_login import current_user
    from app.utils.manager_utils import translate_manager

    text = translate_manager(text, session['LANGUAGE_OPTION_CHOOSE'])
    send_sse_message("bar", "Elaboro Traduzione", 100, "trans")
    path_trascription = write_file(text, "translate_folder")

    words = text.split()
    if len(words) > 100:
        result_print = " ".join(words[:100])
        result_print += " ...."
    else:
        result_print = text
    current_user.user_elements_translate.append({'response_text': result_print,
                                                 'link_text': "<a href='" + path_trascription + "' "
                                                 "id='cont_ai_chat_file' style='display:block;' download> <pre> Scarica il File " + filename + ": " +
                                                 " <i class='fa-solid fa-file'></i></pre> </a>"})


def file_audio_builder(text, audio_opt, audio_lang, filename):
    # Dato un testo esegue l'opzione sul testo e crea la risposta grafica
    from flask_login import current_user
    from app.utils.manager_utils import translate_manager
    try:
        if num_tokens_from_messages(text) >= 15500:
            raise Exception("La trascrizione supera il limite di Token. TOKEN : " + str(num_tokens_from_messages(text)))

        if audio_opt == 'Trascrizione':
            result = text
        elif audio_opt == 'Traduzione':
            result = translate_manager(text, audio_lang, 'audio')
        else:
            result = audio_text_call(audio_opt, text)

        words = result.split()
        result_print = " ".join(words[:100]) + " ...." if len(words) > 100 else result

        if audio_opt == 'Trascrizione':
            path_trascription = write_file(result, "audio_folder")
            current_user.user_elements_audio.append({'response_text': result_print,
                                                     'link_text': "<a href='" + path_trascription + "' id='cont_ai_chat_file' \
                                               style='display:block;' download> <pre> Scarica la Trascrizione di " +
                                                                  filename + " : " +
                                                                  " <i class='fa-solid fa-file'></i></pre> </a>"})
        else:
            path_trascription_opt = write_file(result, "audio_folder")
            path_trascription = write_file(text, "audio_folder")
            current_user.user_elements_audio.append(
                {'response_text': result_print,
                 'link_text': "<a href='" + path_trascription_opt + "' ""id='cont_ai_chat_file' \
                  style='display:block;' download> <pre> Scarica il file : " \
                                                                    " <i class='fa-solid fa-file'></i></pre>"
                                                                    "<a href='" + path_trascription + "' id='cont_ai_chat_file' \
                  style='display:block ;' class='mt-2' download> <pre> Scarica la Trascrizione di " + filename + " : " +
                              " <i class='fa-solid fa-file'></i></pre> </a>"})

    except Exception:
        if audio_opt == 'Trascrizione':
            words = text.split()
            result_print = " ".join(words[:100]) + " ...." if len(words) > 100 else text
            path_trascription = write_file(text, "audio_folder")
            current_user.user_elements_audio.append({'response_text': result_print,
                                                     'link_text': "<a href='" + path_trascription +
                                                                  "' id='cont_ai_chat_file style='display:block;' download> <pre> " \
                                                                  "Scarica la Trascrizione di " + filename + " :  <i "
                                                                                                             "class='fa-solid "
                                                                                                             "fa-file'></i></pre> "
                                                                                                             "</a>"})
        else:
            count = 0
            progress = 75
            if audio_opt == 'Traduzione':
                segments = split_text_into_sections(text, 2000)
                with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                    translate_call_with_lang = functools.partial(translate_file_text_with_gpt, audio_lang)

                    futures = [executor.submit(translate_call_with_lang, segment) for segment in segments]

                    translate_transcript = []
                    for future in futures:
                        try:
                            translate_transcript.append(future.result(timeout=250))
                            count += 1
                            progress += 25 / len(segments)
                            send_sse_message("bar", f"Traduzione : {count}/{len(segments)}", progress, "audio")
                        except Exception as e:
                            executor.shutdown(wait=False, cancel_futures=True)
                            print(f"Errore durante la traduzione: {str(e)}")
                            raise

                    result = ''.join(translate_transcript)

            else:
                segments = split_text_into_sections(text, 13000)

                with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                    translate_call_with_opt = functools.partial(audio_text_call, audio_opt)
                    futures = [executor.submit(translate_call_with_opt, segment) for segment in segments]

                    transcripts = []

                    for future in futures:
                        try:
                            transcripts.append(future.result(timeout=140))
                            count += 1
                            progress += 25 / len(segments)
                            send_sse_message("bar", f"Elaborazione : {count}/{len(segments)}", progress, "audio")
                        except Exception as e:
                            executor.shutdown(wait=False, cancel_futures=True)
                            print(f"Errore durante le operazioni: {str(e)}")
                            raise
                    result = ''.join(transcripts)

            words = result.split()
            result_print = " ".join(words[:100]) + " ...." if len(words) > 100 else result

            path_trascription_opt = write_file(result, "audio_folder")
            path_trascription = write_file(text, "audio_folder")
            current_user.user_elements_audio.append(
                {'response_text': result_print,
                 'link_text': "<a href='" + path_trascription_opt + "' ""id='cont_ai_chat_file' \
                             style='display:block;' download> <pre> Scarica il file : " \
                                                                    " <i class='fa-solid fa-file'></i></pre>"
                                                                    "<a href='" + path_trascription + "' id='cont_ai_chat_file' \
                             style='display:block ;' class='mt-2' download> <pre> Scarica la Trascrizione " + filename + " : " +
                              " <i class='fa-solid fa-file'></i></pre> </a>"})
