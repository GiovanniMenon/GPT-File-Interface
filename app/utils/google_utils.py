import re
from googletrans import Translator

def get_language_code(language_name):
    language_map = {
        "Chinese": "zh",
        "Korean": "ko",
        "Danish": "da",
        "Finnish": "fi",
        "French": "fr",
        "Japanese": "ja",
        "Greek": "el",
        "English": "en",
        "Italian": "it",
        "Norwegian": "no",
        "Dutch": "nl",
        "Polish": "pl",
        "Portuguese": "pt",
        "Russian": "ru",
        "Spanish": "es",
        "Swedish": "sv",
        "German": "de"
    }

    return language_map.get(language_name, "en")


def translate_text_with_google(lang, text):
    translator = Translator()
    return translator.translate(text,  dest=get_language_code(lang)).text
