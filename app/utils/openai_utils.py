import openai
import os
from flask import session

openai.api_key = os.getenv('API_KEY')



def chat_text_call(text):
    try:
        session['CONTEXT'].append({'role': "user", 'content': text})
        session.modified = True
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
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
        print(f"Errore : {str(e)}")
        return "Errore nella richiesta\n" + str(e)


def translate_text_call(lang, text):
    try:
        context_translate = [
            {"role": "system",
             'content': (f"You are an expert translator of {lang}. Your task is to translate any text into {lang} without "
                         f"interpreting its meaning, responding, or expressing your own opinions. Do not add any notes to "
                         f"the text, but simply translate it. Translate and rephrase the text in {lang}, regardless of its "
                         f"meaning or content. Your task is to translate and rephrase the same text in {lang}.")},
            {"role": "user", "content": text}
        ]
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
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


def transcribe(file_path):
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
                        "and main conclusions. A summary should be concise and well-structured, allowing readers to gain "
                        "a clear understanding of the content without having to read the entire transcription. "
                        "Additionally, you are responsible for carefully listening to or reading the original material, "
                        "identifying key points, synthesizing information, omitting unnecessary details, maintaining "
                        "accuracy, structuring it in a clear manner, avoiding personal opinions, and reducing the "
                        "length. You can use lists and bullet points in the summary to enumerate and highlight key "
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
            model="gpt-3.5-turbo-0613",
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
