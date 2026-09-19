from deep_translator import GoogleTranslator
from deep_translator.exceptions import TooManyRequests, TranslationNotFound, LanguageNotSupportedException
from app.schemas.translation import TranslationResponse, Language
from fastapi import HTTPException
import time


SUPPORTED_LANGUAGES = {
    "af": "Afrikaans", "sq": "Albanian", "am": "Amharic", "ar": "Arabic",
    "az": "Azerbaijani", "eu": "Basque", "be": "Belarusian", "bn": "Bengali",
    "bs": "Bosnian", "bg": "Bulgarian", "ca": "Catalan", "ceb": "Cebuano",
    "ny": "Chichewa", "zh-cn": "Chinese (Simplified)", "zh-tw": "Chinese (Traditional)",
    "co": "Corsican", "hr": "Croatian", "cs": "Czech", "da": "Danish",
    "nl": "Dutch", "en": "English", "eo": "Esperanto", "et": "Estonian",
    "tl": "Filipino", "fi": "Finnish", "fr": "French", "fy": "Frisian",
    "gl": "Galician", "ka": "Georgian", "de": "German", "el": "Greek",
    "gu": "Gujarati", "ht": "Haitian Creole", "ha": "Hausa", "haw": "Hawaiian",
    "iw": "Hebrew", "hi": "Hindi", "hmn": "Hmong", "hu": "Hungarian",
    "is": "Icelandic", "ig": "Igbo", "id": "Indonesian", "ga": "Irish",
    "it": "Italian", "ja": "Japanese", "jw": "Javanese", "kn": "Kannada",
    "kk": "Kazakh", "km": "Khmer", "ko": "Korean", "ku": "Kurdish",
    "ky": "Kyrgyz", "lo": "Lao", "la": "Latin", "lv": "Latvian",
    "lt": "Lithuanian", "lb": "Luxembourgish", "mk": "Macedonian",
    "mg": "Malagasy", "ms": "Malay", "ml": "Malayalam", "mt": "Maltese",
    "mi": "Maori", "mr": "Marathi", "mn": "Mongolian", "my": "Myanmar (Burmese)",
    "ne": "Nepali", "no": "Norwegian", "ps": "Pashto", "fa": "Persian",
    "pl": "Polish", "pt": "Portuguese", "pa": "Punjabi", "ro": "Romanian",
    "ru": "Russian", "sm": "Samoan", "gd": "Scots Gaelic", "sr": "Serbian",
    "st": "Sesotho", "sn": "Shona", "sd": "Sindhi", "si": "Sinhala",
    "sk": "Slovak", "sl": "Slovenian", "so": "Somali", "es": "Spanish",
    "su": "Sundanese", "sw": "Swahili", "sv": "Swedish", "tg": "Tajik",
    "ta": "Tamil", "te": "Telugu", "th": "Thai", "tr": "Turkish",
    "uk": "Ukrainian", "ur": "Urdu", "uz": "Uzbek", "vi": "Vietnamese",
    "cy": "Welsh", "xh": "Xhosa", "yi": "Yiddish", "yo": "Yoruba", "zu": "Zulu",
}


def translate_text(text: str, source_lang: str, target_lang: str) -> TranslationResponse:
    """Translate text using Google Translate via deep-translator.
    Retries once after 2 seconds on rate limit, then raises HTTP 429.
    """
    translator = GoogleTranslator(source=source_lang, target=target_lang)

    for attempt in range(2):  # try up to 2 times
        try:
            translated = translator.translate(text)
            return TranslationResponse(
                original_text=text,
                translated_text=translated,
                source_language=source_lang,
                target_language=target_lang,
            )
        except TooManyRequests:
            if attempt == 0:
                time.sleep(2)  # wait 2s then retry once
                continue
            raise HTTPException(
                status_code=429,
                detail="Google Translate rate limit reached. Please wait a moment and try again.",
            )
        except LanguageNotSupportedException:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language pair: '{source_lang}' → '{target_lang}'.",
            )
        except TranslationNotFound:
            raise HTTPException(
                status_code=422,
                detail="Translation could not be found for the given text.",
            )
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Translation service unavailable: {str(e)}",
            )


def get_supported_languages() -> list[Language]:
    """Return all supported languages as a list of {code, name} objects."""
    return [Language(code=code, name=name) for code, name in SUPPORTED_LANGUAGES.items()]
