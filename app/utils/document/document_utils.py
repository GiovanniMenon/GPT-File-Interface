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
    translations = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        translate_call_with_lang = functools.partial(translate_document_text_call, lang)
        translations = list(executor.map(translate_call_with_lang, parts))

    return translations


def docx_file_translate_google(doc_path, lang, part):
    doc = Document(doc_path)
    counter = 0
    translations = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        translate_call_with_lang = functools.partial(translate_text_with_google, lang)
        translations = list(executor.map(translate_call_with_lang, part))

    return translations
