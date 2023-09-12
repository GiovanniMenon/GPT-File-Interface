import concurrent.futures
import functools
import unicodedata

from app.utils.openai_utils import translate_document_text_call


def contains_only_punctuation(text):
    return all(unicodedata.category(char).startswith('P') for char in text)


def docx_file_translate(parts, lang):
    translations = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        translate_call_with_lang = functools.partial(translate_document_text_call, lang)
        results = list(executor.map(translate_call_with_lang, parts.keys()))

    for original, translation in results:
        translations[original] = translation

    return translations