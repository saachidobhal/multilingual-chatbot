from deep_translator import GoogleTranslator
from langdetect import detect
from functools import lru_cache

SUPPORTED_LANGS = {"hi", "ta", "bn", "mr", "te", "ur", "en", "gu", "pa", "kn", "ml"}

def detect_language(text):
    try:
        # Hinglish fix: if text has Latin script but common Hindi words, treat as Hindi
        hindi_latin_words = {"hai", "hain", "kya", "nahi", "aur", "ka", "ki", "ke",
                             "mein", "se", "ho", "kar", "tha", "thi", "yeh", "woh",
                             "bhi", "to", "na", "mat", "karo", "kuch", "sab", "log"}
        words = set(text.lower().split())
        if len(words & hindi_latin_words) >= 2:
            return "hi"

        lang = detect(text)

        if lang not in SUPPORTED_LANGS:
            return "en"

        return lang
    except:
        return "en"

@lru_cache(maxsize=512)
def translate_to_english(text):
    try:
        if detect_language(text) == "en":
            return text
        return GoogleTranslator(source="auto", target="en").translate(text)
    except:
        return text

@lru_cache(maxsize=512)
def translate_from_english(text, target_lang):
    try:
        if target_lang == "en":
            return text
        return GoogleTranslator(source="en", target=target_lang).translate(text)
    except:
        return text