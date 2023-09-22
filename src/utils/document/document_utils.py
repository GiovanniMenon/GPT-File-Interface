import concurrent.futures
import functools

import unicodedata

from src.utils.message_utils import send_sse_message
from src.utils.openai_utils import translate_document_text_call


def contains_only_punctuation(text):
    # Controlla che il testo non abbia solo punteggiatura

    return all(unicodedata.category(char).startswith('P') for char in text)


def docx_file_translate_gpt(segments, lang):
    # Dati dei segmenti per ogni segmento esegue una chiamata all'API e ritorna i segmenti tradotti

    progress = 40
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        translate_call_with_lang = functools.partial(translate_document_text_call, lang)

        futures = [executor.submit(translate_call_with_lang, segment) for segment in segments]

        translations = []
        count = 0
        for future in futures:
            try:
                translations.append(future.result(timeout=150))
                count += 1
                progress += 55 / len(segments)
                send_sse_message("bar", f"Traduzione: {count}/{len(segments)}", progress, "trans")
            except Exception as e:
                executor.shutdown(wait=False, cancel_futures=True)
                print(f"Errore durante la traduzione: {str(e)}")
                raise e

    return translations
