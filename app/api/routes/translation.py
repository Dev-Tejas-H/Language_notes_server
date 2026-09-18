from fastapi import APIRouter, Depends
from app.schemas.translation import TranslationRequest, TranslationResponse, TTSRequest, SupportedLanguagesResponse
from app.services.translation_service import translate_text, get_supported_languages
from app.services.tts_service import generate_tts_audio
from app.utils.auth_deps import get_current_user
from app.models.user import User
from fastapi.responses import FileResponse
import os

router = APIRouter(prefix="/translate", tags=["Translation"])


@router.post("/", response_model=TranslationResponse)
def translate(
    request: TranslationRequest,
    current_user: User = Depends(get_current_user),
):
    """Translate text from English (or any language) to the target language."""
    return translate_text(request.text, request.source_language, request.target_language)


@router.get("/languages", response_model=SupportedLanguagesResponse)
def supported_languages():
    """Get all supported translation language codes and names."""
    return SupportedLanguagesResponse(languages=get_supported_languages())


@router.post("/tts")
def text_to_speech(
    request: TTSRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate TTS audio for a given text and language. Returns the audio file."""
    audio_path = generate_tts_audio(request.text, request.language, request.slow)
    return FileResponse(
        path=audio_path,
        media_type="audio/mpeg",
        filename=os.path.basename(audio_path),
    )
