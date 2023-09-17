import concurrent.futures
import functools

import unicodedata

from docx import Document
from app.utils.google_utils import translate_text_with_google
from app.utils.openai_utils import translate_document_text_call


def contains_only_punctuation(text):
    return all(unicodedata.category(char).startswith('P') for char in text)


def docx_file_translate_gpt(segments, lang):
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        translate_call_with_lang = functools.partial(translate_document_text_call, lang)

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

    return translations


def docx_file_translate_google( part , lang):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        translate_call_with_lang = functools.partial(translate_text_with_google, lang)
        translations = list(executor.map(translate_call_with_lang, part))

    return translations
