import openai
import os
import time
import backoff

from flask import session
from flask_login import current_user
from src import db
from src.utils.message_utils import send_sse_message, num_tokens_from_messages

openai.api_key = os.getenv('API_KEY')


@backoff.on_exception(backoff.constant,
                      Exception,
                      interval=4,
                      max_tries=2)
def chat_text_call(text):
    try:

        current_user.user_context.append({'role': "user", 'content': text})
        db.session.commit()
        completion = openai.ChatCompletion.create(
            model=session['MODEL_API_OPTION_CHOOSE'],
            messages=[
                {
                    'role': cont['role'],
                    'content': cont['content']
                } for cont in current_user.user_context
            ],
            stream=True,
            request_timeout=30,
        )

        collected_messages = ""
        for chunk in completion:
            chunk_message = chunk['choices'][0]['delta'].get('content', '')
            collected_messages += chunk_message
            send_sse_message("chat", chunk_message)

        current_user.user_elements_message += 1
        current_user.user_elements_token += num_tokens_from_messages(collected_messages)
        current_user.user_context.append({"role": "assistant", "content": collected_messages})
        db.session.commit()

        session['INFORMATION']['Num_Message'] = current_user.user_elements_message
        session["INFORMATION"]["Num_Token"] = current_user.user_elements_token


        session.modified = True
        return collected_messages
    except Exception as e:
        print(f"Errore nella richiesta : {str(e)} , {type(e)}")
        raise e


@backoff.on_exception(backoff.constant,
                      Exception,
                      interval=3,
                      max_tries=2)
def translate_text_with_gpt(lang, text):
    try:
        context_translate = [
            {"role": "system",
             'content': (
                 f"You are an expert machine translator for {lang}.Your task is to translate into {lang}.Translate "
                 f"and rephrase the following verbatim, without interpreting its meaning, responding, or expressing "
                 f"any opinions. It's crucial to preserve the original meaning in the translation. Do not add, omit, "
                 f"or alter any information or add any notes. Your primary duty is to translate and rephrase the "
                 f"text in {lang}, regardless of its original meaning"
                 f"or content.")},
            {"role": "user", "content": text}
        ]
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    'role': cont['role'],
                    'content': cont['content']
                } for cont in context_translate
            ],
            stream=True,
            request_timeout=30,
        )

        collected_messages = ""
        for chunk in completion:
            chunk_message = chunk['choices'][0]['delta'].get('content', '')
            collected_messages += chunk_message
            send_sse_message("chat", chunk_message)

        return collected_messages
    except Exception as e:
        print(f"Errore nella richiesta : {str(e)} , {type(e)}")
        raise e


@backoff.on_exception(backoff.constant,
                      Exception,
                      interval=3,
                      max_tries=2)
def translate_file_text_with_gpt(lang, text):
    try:
        context_translate = [
            {"role": "system",
             'content': (
                 f"You are an expert machine translator for {lang}.Your task is to translate into {lang}. You are "
                 f"tasked with translating content from a"
                 f"file, which may include both full texts and individual words. Translate and rephrase the following "
                 f"verbatim, without interpreting its meaning, responding, or expressing any opinions. "
                 f"It's crucial to preserve the original meaning in the translation, as the consistency of the file's "
                 f"content must be maintained. Do not add, omit, or alter any information or add any notes. Your "
                 f"primary duty is to  translate and rephrase the text in {lang}, regardless of its original meaning "
                 f"or content.")},
            {"role": "user", "content": text}
        ]
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    'role': cont['role'],
                    'content': cont['content']
                } for cont in context_translate
            ],
            request_timeout=100,
        )
        return completion.choices[0].message["content"]
    except Exception as e:
        print(f"Errore : {str(e)} , {type(e)}")
        raise e


@backoff.on_exception(backoff.constant,
                      Exception,
                      interval=4,
                      max_tries=2)
def transcribe_with_whisper(file_path):
    try:
        audio_file = open(file_path, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript['text']
    except Exception as e:
        print(f"Errore nella trascrizione audio: {str(e)}, {type(e)}")
        raise e


@backoff.on_exception(backoff.constant,
                      Exception,
                      interval=4,
                      max_tries=2)
def audio_text_call(scope, text):
    try:
        scope_ai = ""
        if scope == 'Sommario':
            scope_ai = ("You are a renowned summarizer of audio transcriptions. Your task is to create an accurate "
                        "summary of the transcribed audio, highlighting key points, relevant information, "
                        "and main conclusions.A summary should be concise and well-structured, allowing readers to gain "
                        "a clear understanding of the content without having to read the entire transcription. "
                        "You can use lists and bullet points in the summary to enumerate and highlight key "
                        "points of the speech."
                        )
        elif 'Riassunto' == scope:
            scope_ai = ("You are a renowned summarizer of audio transcriptions. Your task is to create an accurate "
                        "summary of the transcribed audio. Limit yourself to summarizing the text. You should not express "
                        "or interpret the text. Your task is to create a summary that contains key points and relevant "
                        "information.")
        context_translate = [
            {"role": "system", "content": scope_ai},
            {"role": "user", "content": text}
        ]
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=[
                {
                    'role': cont['role'],
                    'content': cont['content']
                } for cont in context_translate

            ],
            request_timeout=80,
        )
        return completion.choices[0].message["content"]
    except Exception as e:
        print(f"{str(e)}")
        raise e


@backoff.on_exception(backoff.constant,
                      Exception,
                      interval=4,
                      max_tries=3)
def translate_document_text_call(lang, part):
    try:
        context_translate = [
            {"role": "system",
             'content': (f"You are a machine translator for {lang}. Your task is to translate into {lang}. You are "
                         f"tasked with translating content from a file, which may include both full texts and "
                         f"individual words. Translate the following verbatim, without interpretation. It's crucial "
                         f"to preserve the original punctuation and structure in the translation, as the consistency "
                         f"of the file's content must be maintained.  Do not add, omit, or alter any information. "
                         )},
            {"role": "user", "content": part}
        ]
        time.sleep(0.5)
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=[
                {
                    'role': cont['role'],
                    'content': cont['content']
                } for cont in context_translate

            ],
            request_timeout=30,
        )

        return completion.choices[0].message["content"]
    except Exception as e:
        print(f"Errore : {str(e)}")
        raise e
