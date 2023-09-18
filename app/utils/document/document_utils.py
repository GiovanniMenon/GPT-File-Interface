import concurrent.futures
import functools

import unicodedata

from docx import Document
from app.utils.google_utils import translate_text_with_google
from app.utils.message_utils import send_sse_message
from app.utils.openai_utils import translate_document_text_call


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
                progress += 55/len(segments)
                send_sse_message(f"Traduzione: {count}/{len(segments)}" , progress , "trans") 
            except Exception as e:
                executor.shutdown(wait=False, cancel_futures=True)
                print(f"Errore durante la traduzione: {str(e)}")
                raise

    return translations


def docx_file_translate_google( part , lang):
    # Per ogni parte richiama la traduzione con la google Ai
    # Da rimuovere per il basso rate limit della libreria
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        translate_call_with_lang = functools.partial(translate_text_with_google, lang)
        translations = list(executor.map(translate_call_with_lang, part))

    return translations
