
from markupsafe import escape
import tiktoken
import re


def decode(input_string):
    # Data una stringa sostituisce a ''' con i tag html di pre e code
    # Serve per evidenziare le parti di codice che vengono ritornate
    
    segments = re.split(r'```(.*?)```', input_string, flags=re.DOTALL)

    processed_segments = []

    for i, segment in enumerate(segments):
        processed_segments.append(
            f"<pre><code>{escape(segment)}</code></pre>") if i % 2 != 0 else processed_segments.append(escape(segment))
    return ''.join(processed_segments)


def num_tokens_from_messages(string, model="gpt-3.5-turbo-0613"):
    # Dato un testo ritorna il numero di token
    
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    tokenized_string = encoding.encode(string)
    return len(tokenized_string)


def split_text_into_sections(text, max_tokens, model="gpt-3.5-turbo-0613"):
    # Dato un testo restituisce una lista con il testo diviso in parti che non superano il max_tokens
    
    sections = []
    current_section = ""
    current_section_tokens = 0

    paragraphs = text.split(" ")

    for paragraph in paragraphs:
        paragraph_tokens = num_tokens_from_messages(paragraph, model)

        if current_section_tokens + paragraph_tokens > max_tokens-50 and \
                ("." in paragraph or current_section_tokens + paragraph_tokens > max_tokens + 50):
            current_section += paragraph
            sections.append(current_section)
            current_section = ""
            current_section_tokens = 0
        else:
            current_section += paragraph + ' '
            current_section_tokens += paragraph_tokens

    if current_section:
        sections.append(current_section)

    return sections


def send_sse_message(message, progress, opt):
    # Dato un messaggio, progresso e opt effettua una richiesta SSE al client

    from flask import current_app as app
    from flask import session
    data = {'index': message, 'progress' : progress, "opt": opt}
    
    with app.app_context():
        from flask_sse import sse
        sse.publish(data, channel=session["ID_USER"])
