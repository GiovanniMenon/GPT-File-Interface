
import openai
import os
from flask import session
import time
MAX_TRIES = 4
openai.api_key = os.getenv('API_KEY')


def chat_text_call(text):
    for attempt in range(MAX_TRIES):
        try:
            session['CONTEXT'].append({'role': "user", 'content': text})
            session.modified = True
            completion = openai.ChatCompletion.create(
                model=session['MODEL_API_OPTION_CHOOSE'],
                messages=[
                    {
                        'role': cont['role'],
                        'content': cont['content']
                    } for cont in session['CONTEXT']

                ])
            session['CONTEXT'].append({"role": "assistant", "content": completion.choices[0].message["content"]})
            session.modified = True
            session['INFORMATION']['Num_Message'] = session['INFORMATION']['Num_Message'] + 1
            session["INFORMATION"]["Num_Token"] = completion.usage["total_tokens"]
            session.modified = True

            return completion.choices[0].message["content"]
        except Exception as e:
            if 'Bad gateway' in str(e) and attempt < MAX_TRIES - 1:
                continue
            print(f"Errore : {str(e)}")
            if 'Bad gateway' in str(e):
                return f"Errore : Bad gateway. Massimo numero di tentativi ({MAX_TRIES}) raggiunto."
            else:
                return f"Errore nella richiesta\n{str(e)}"


def translate_text_with_gpt(lang, text):
    for attempt in range(MAX_TRIES):
        try:
            context_translate = [
                {"role": "system",
                 'content': (f"You are an expert machine translator for {lang}. You are tasked with translating content from a "
                             f"file, which may include both full texts and individual words. Translate and rephrase the following "
                             f"verbatim, without interpreting its meaning, responding, or expressing any opinions. It's crucial to preserve "
                             f"the original meaning in the translation, as the consistency of the file's content must be "
                             f"maintained. Do not add, omit, or alter any information or add any notes. Your primary duty is to "
                             f"translate and rephrase the text in {lang}, regardless of its original meaning or content.")},
                {"role": "user", "content": text}
            ]
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        'role': cont['role'],
                        'content': cont['content']
                    } for cont in context_translate

                ])
            return completion.choices[0].message["content"]
        except Exception as e:
            if 'Bad gateway' in str(e) and attempt < MAX_TRIES - 1:
                continue
            print(f"Errore : {str(e)}")
            if 'Bad gateway' in str(e):
                return f"Errore : Bad gateway. Massimo numero di tentativi ({MAX_TRIES}) raggiunto."
            else:
                return f"Errore nella richiesta\n{str(e)}"


def transcribe_with_whisper(file_path):
    try:
        audio_file = open(file_path, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript['text']
    except Exception as e:
        print(f"Errore : {str(e)}")
        return "Errore nella trascrizione: \n" + str(e)


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

            ])
        return completion.choices[0].message["content"]
    except Exception as e:
        print(f"Errore : {str(e)}")
        return "Errore nella richiesta\n" + str(e)


def translate_document_text_call(lang, part):
    for attempt in range(MAX_TRIES):
        try:
            context_translate = [
                {"role": "system",
                 'content': (f"You are a machine translator for {lang}. You are tasked with translating content from a "
                             f"file, which may include both full texts and individual words. Translate the following "
                             f"verbatim, without interpretation. It's crucial to preserve the original punctuation and "
                             f"structure in the translation, as the consistency of the file's content must be maintained. "
                             f"Do not add, omit, or alter any information."
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

                ])

            return completion.choices[0].message["content"]
        except Exception as e:
            if 'Bad gateway' in str(e) and attempt < MAX_TRIES - 1:
                continue
            print(f"Errore : {str(e)}")
            if 'Bad gateway' in str(e):
                return f"Errore : Bad gateway. Massimo numero di tentativi ({MAX_TRIES}) raggiunto."
            else:
                return f"Errore nella richiesta\n{str(e)}"