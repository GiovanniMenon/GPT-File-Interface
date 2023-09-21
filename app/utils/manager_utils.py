import concurrent.futures
import functools
import os

from flask import session

from app.utils.document.document_builder import document_translate_builder
from app.utils.file.file_builder import file_chat_builder, file_translate_builder, file_audio_builder
from app.utils.file.file_utils import is_audio, path_file, remove_selected_file, \
    save_file, compress_audio, split_audio
from app.utils.message_utils import num_tokens_from_messages, split_text_into_sections, send_sse_message
from app.utils.openai_utils import translate_text_with_gpt, transcribe_with_whisper, translate_file_text_with_gpt
from werkzeug.utils import secure_filename

from app.utils.parser.parser import extract_file_content


def file_manager(file, scope="chat", opt="", audio_lang=""):
    # Dato un file, scope e le opzioni richiama i corrispettivi builder e parser per gestirlo

    path_ = path_file(file)
    filename = file.filename
    save_file(file, path_)

    if scope == 'audio':

        text = audio_manager(path_)
    else:
        text = extract_file_content(path_, secure_filename(filename))

    if scope == "chat":
        file_chat_builder(text, filename)
    elif scope == "translate":
        if opt == 'documento':
            document_translate_builder(path_, filename)
        else:
            file_translate_builder(text, filename)
    elif scope == "audio":
        file_audio_builder(text, opt, audio_lang, filename)
    remove_selected_file(path_)


def translate_manager(text, lang, opt="trans"):
    # Dato un testo ritorna la sua traduzione
    if num_tokens_from_messages(text) > 500 and not opt == "text":
        segments = split_text_into_sections(text, 350)
        progress = 30
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            translate_call_with_lang = functools.partial(translate_file_text_with_gpt, lang)
            futures = [executor.submit(translate_call_with_lang, segment) for segment in segments]
            translations = []
            count = 0
            for future in futures:
                try:
                    translations.append(future.result(timeout=150))
                    count += 1
                    progress += 60 / len(segments)
                    send_sse_message("bar", f"Traduzione : {count}/{len(segments)}", progress, opt)
                except Exception as e:
                    executor.shutdown(wait=False, cancel_futures=True)
                    print(f"Errore durante la traduzione: {str(e)}")
                    raise e
        translated_text = ''.join(translations)
        return translated_text
    else:
        send_sse_message("bar", "Traduzione in corso", 90, "trans")
        return translate_text_with_gpt(session['LANGUAGE_OPTION_CHOOSE'], text)


def audio_manager(path_):
    # Dato un file audio o mp4 ritorna la sua trascrizione
    if os.path.getsize(path_) / (1024 * 1024) > 25 or not (is_audio(path_)):
        segments = split_audio(compress_audio(path_))
        progress = 50
        count = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(transcribe_with_whisper, segment) for segment in segments]

            transcripts = []

            for future in futures:
                try:
                    transcripts.append(future.result(timeout=250))
                    count += 1
                    progress += 25 / len(segments)
                    send_sse_message("bar", f"Trascrizione : {count}/{len(segments)}", progress, "audio")
                except Exception as e:
                    executor.shutdown(wait=False, cancel_futures=True)
                    print(f"Errore durante la traduzione: {str(e)}")
                    raise e

        transcripts_text = ''.join(transcripts)
        return transcripts_text
    else:
        send_sse_message("bar", "Elaborazione dell trascrizione", 80, 'audio')

        return transcribe_with_whisper(path_)
