from pydantic import BaseModel
from typing import Optional


class TranslationRequest(BaseModel):
    text: str
    source_language: str = "en"
    target_language: str


class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str


class TTSRequest(BaseModel):
    text: str
    language: str = "en"
    slow: bool = False


class SupportedLanguagesResponse(BaseModel):
    languages: dict  # code -> name
