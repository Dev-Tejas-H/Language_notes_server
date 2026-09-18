from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import aiofiles
import os
import uuid

from app.db.database import get_db
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse, NoteListResponse
from app.services import note_service, tts_service
from app.core.config import settings
from app.utils.auth_deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.get("/", response_model=NoteListResponse)
def list_notes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notes, total = note_service.get_notes(db, current_user.id, skip, limit, category, search)
    return NoteListResponse(notes=notes, total=total)


@router.post("/", response_model=NoteResponse, status_code=201)
def create_note(
    note_in: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return note_service.create_note(db, current_user.id, note_in)


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return note_service.get_note_by_id(db, note_id, current_user.id)


@router.patch("/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: str,
    note_update: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return note_service.update_note(db, note_id, current_user.id, note_update)


@router.delete("/{note_id}", status_code=204)
def delete_note(
    note_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note_service.delete_note(db, note_id, current_user.id)


@router.post("/{note_id}/audio", response_model=NoteResponse)
async def upload_voice_message(
    note_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a voice message (audio file) and attach it to a note."""
    note = note_service.get_note_by_id(db, note_id, current_user.id)

    allowed_types = {"audio/mpeg", "audio/wav", "audio/ogg", "audio/m4a", "audio/mp4"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid audio file type")

    os.makedirs(settings.AUDIO_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename)[1] or ".mp3"
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(settings.AUDIO_DIR, filename)

    async with aiofiles.open(file_path, "wb") as out:
        content = await file.read()
        await out.write(content)

    note.audio_file_path = file_path
    db.commit()
    db.refresh(note)
    return note


@router.post("/{note_id}/generate-audio", response_model=NoteResponse)
def generate_tts_for_note(
    note_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Auto-generate TTS audio from the note's original text."""
    note = note_service.get_note_by_id(db, note_id, current_user.id)
    audio_path = tts_service.generate_tts_audio(
        text=note.original_text,
        language=note.source_language or "en",
    )
    note.audio_file_path = audio_path
    db.commit()
    db.refresh(note)
    return note
