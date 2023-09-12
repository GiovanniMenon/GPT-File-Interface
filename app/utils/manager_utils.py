
from markupsafe import escape
import tiktoken
import re


def decode(input_string):
    segments = re.split(r'```(.*?)```', input_string, flags=re.DOTALL)

    processed_segments = []

    for i, segment in enumerate(segments):
        processed_segments.append(
            f"<pre><code>{escape(segment)}</code></pre>") if i % 2 != 0 else processed_segments.append(escape(segment))
    return ''.join(processed_segments)


def num_tokens_from_messages(string, model="gpt-3.5-turbo-0613"):
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    tokenized_string = encoding.encode(string)
    return len(tokenized_string)


def split_text_into_sections(text, max_tokens, model="gpt-3.5-turbo-0613"):
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
    for sec in sections:
        print(f"{num_tokens_from_messages(sec)}")

    return sections
