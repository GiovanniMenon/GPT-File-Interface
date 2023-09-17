import concurrent.futures
import functools
import os

from flask import session

from app.utils.document.document_builder import document_translate_builder
from app.utils.file.file_builder import file_chat_builder, file_translate_builder, file_audio_builder
from app.utils.file.file_utils import is_audio, path_file, remove_selected_file, \
    save_file, compress_audio, split_audio
from app.utils.google_utils import translate_text_with_google
from app.utils.message_utils import num_tokens_from_messages, split_text_into_sections
from app.utils.openai_utils import translate_text_with_gpt, transcribe_with_whisper
from werkzeug.utils import secure_filename

from app.utils.parser.parser import extract_file_content


def file_manager(file, scope="chat", opt="", audio_lang=""):
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
            document_translate_builder(path_)
        else:
            file_translate_builder(text)
    elif scope == "audio":
        file_audio_builder(text, opt, audio_lang)
    remove_selected_file(path_)


def translate_manager(text, lang, model="GPT-AI", filename="Utente"):
    if model == 'Google-AI':
        return translate_text_with_google(lang, text)
    else:
        if num_tokens_from_messages(text) > 500:
            segments = split_text_into_sections(text, 350)

            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                translate_call_with_lang = functools.partial(translate_text_with_gpt, lang)

                futures = [executor.submit(translate_call_with_lang, segment) for segment in segments]

                translations = []
                count = 0
                for future in futures:
                    try:
                        translations.append(future.result(timeout=150))
                        count += 1
                        print(f"Tradotti {count} di {len(segments)} elementi.")
                    except Exception as e:
                        executor.shutdown(wait=False, cancel_futures=True)
                        print(f"Errore durante la traduzione: {str(e)}")
                        return -1

            translated_text = ''.join(translations)
            return translated_text
        else:
            return translate_text_with_gpt(session['LANGUAGE_OPTION_CHOOSE'], text)


def audio_manager(path_, filename="Utente"):
    if os.path.getsize(path_) / (1024 * 1024) > 25 or not (is_audio(filename)):
        segments = split_audio(compress_audio(path_))

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(transcribe_with_whisper, segment) for segment in segments]

            transcripts = []

            count = 0

            for future in futures:
                try:
                    transcripts.append(future.result(timeout=250))
                    count += 1
                    print(f"Trascritti {count} di {len(segments)} elementi.")
                except Exception as e:
                    executor.shutdown(wait=False, cancel_futures=True)
                    print(f"Errore durante la traduzione: {str(e)}")
                    return -1

        transcripts_text = ''.join(transcripts)
        return transcripts_text
    else:
        return transcribe_with_whisper(path_)
