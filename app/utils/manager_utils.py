
import time
import concurrent.futures
import functools
import os

from flask import session
from app.utils.file.file_builder import file_chat_builder, file_translate_builder, file_audio_builder
from app.utils.file.file_utils import extract_file_content, is_audio, path, performance, remove_selected_file, \
    save_file, compress_audio, create_path
from app.utils.message_utils import num_tokens_from_messages, split_text_into_sections
from app.utils.openai_utils import translate_text_call, audio_text_call, transcribe
from werkzeug.utils import secure_filename


def file_manager(file, scope="chat", audio_opt="", audio_lang=""):
    path_ = path(file)
    filename = file.filename
    save_file(file, path_)

    if scope == 'audio':
        if os.path.getsize(path_) / (1024 * 1024)>25 or not (is_audio(filename)):
            path_ = compress_audio(path_)
        text = transcribe(path_)
    else:
        text = extract_file_content(path_, secure_filename(filename))
    if scope == "chat":
        file_chat_builder(text, filename)
    elif scope == "translate":
        file_translate_builder(text)
    elif scope == "audio":
        file_audio_builder(text, audio_opt, audio_lang)

    remove_selected_file(path_)


def translate_manager(text, lang, filename="Utente"):
    if num_tokens_from_messages(text) > 500:
        segments = split_text_into_sections(text, 350)
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            translate_call_with_lang = functools.partial(translate_text_call, lang)
            results = executor.map(translate_call_with_lang, segments)
            translated_text = ''.join(results)
            end_time = time.time()
            performance(filename, session['LANGUAGE_OPTION_CHOOSE'], end_time - start_time)
            return translated_text
    else:
        return translate_text_call(session['LANGUAGE_OPTION_CHOOSE'], text)


def audio_manager(text, scope, filename="Utente"):
    if num_tokens_from_messages(text) > 500:
        segments = split_text_into_sections(text, 350)
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            audio_text_call_with_arg = functools.partial(audio_text_call, scope)
            results = executor.map(audio_text_call_with_arg, segments)
            audio_text = ''.join(results)
            end_time = time.time()
            performance(filename, session['LANGUAGE_OPTION_CHOOSE'], end_time - start_time)
            return audio_text
    else:
        return audio_text_call(scope, text)
