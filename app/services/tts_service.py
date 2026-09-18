import os
import uuid
from gtts import gTTS
from app.core.config import settings


def ensure_audio_dir():
    os.makedirs(settings.AUDIO_DIR, exist_ok=True)


def generate_tts_audio(text: str, language: str = "en", slow: bool = False) -> str:
    """
    Generate a text-to-speech MP3 file using gTTS.
    Returns the file path relative to server root.
    """
    ensure_audio_dir()
    filename = f"{uuid.uuid4()}.mp3"
    file_path = os.path.join(settings.AUDIO_DIR, filename)

    tts = gTTS(text=text, lang=language, slow=slow)
    tts.save(file_path)

    return file_path


def delete_audio_file(file_path: str) -> bool:
    """Delete an audio file from the filesystem."""
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False
