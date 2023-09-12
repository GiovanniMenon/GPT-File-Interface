import concurrent.futures
import functools
import os

import unicodedata
import re
from docx import Document
from concurrent.futures import as_completed, TimeoutError
from app.utils.file.file_utils import create_path
from app.utils.google_utils import translate_text_with_google
from app.utils.openai_utils import translate_document_text_call


def contains_only_punctuation(text):
    return all(unicodedata.category(char).startswith('P') for char in text)


def docx_file_translate_gpt(parts, lang):
    translations = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        translate_call_with_lang = functools.partial(translate_document_text_call, lang)
        results = list(executor.map(translate_call_with_lang, parts.keys()))

    for original, translation in results:
        translations[original] = translation

    return translations


def docx_file_translate_google(doc_path, lang, type):
    from googletrans import Translator
    doc = Document(doc_path)
    counter = 0
    translator = Translator()

    for paragraph in doc.paragraphs:
        print(f'\r{counter}/{len(doc.paragraphs)}', end='')
        for run in paragraph.runs:
            run.text = translate_text_with_google(lang,run.text)
        counter +=1

    counter_section = 0

    for section in doc.sections:
        print(f'\r{counter}/{len(doc.paragraphs)} {counter_section}/{len(doc.sections)}', end='')
        header = section.header
        for paragraph in header.paragraphs:
            for run in paragraph.runs:
                run.text = translate_text_with_google(lang,run.text)

        footer = section.footer
        for paragraph in footer.paragraphs:
            for run in paragraph.runs:
                run.text = translate_text_with_google(lang,run.text)
        counter_section += 1

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.text = translate_text_with_google(lang,run.text)

    file_path = create_path(".docx", type)
    relative_path = os.path.relpath(file_path, start="myprog")
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    doc.save(file_path)
    return relative_path
