from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, List

from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate


def create_note(db: Session, user_id: str, note_in: NoteCreate, audio_path: Optional[str] = None) -> Note:
    note = Note(
        user_id=user_id,
        title=note_in.title,
        original_text=note_in.original_text,
        translated_text=note_in.translated_text,
        source_language=note_in.source_language,
        target_language=note_in.target_language,
        category=note_in.category,
        tags=note_in.tags,
        audio_file_path=audio_path,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def get_notes(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 50,
    category: Optional[str] = None,
    search: Optional[str] = None,
) -> tuple[List[Note], int]:
    query = db.query(Note).filter(Note.user_id == user_id)
    if category:
        query = query.filter(Note.category == category)
    if search:
        query = query.filter(
            Note.title.ilike(f"%{search}%") | Note.original_text.ilike(f"%{search}%")
        )
    total = query.count()
    notes = query.order_by(Note.created_at.desc()).offset(skip).limit(limit).all()
    return notes, total


def get_note_by_id(db: Session, note_id: str, user_id: str) -> Note:
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


def update_note(db: Session, note_id: str, user_id: str, note_update: NoteUpdate) -> Note:
    note = get_note_by_id(db, note_id, user_id)
    update_data = note_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)
    db.commit()
    db.refresh(note)
    return note


def delete_note(db: Session, note_id: str, user_id: str) -> bool:
    note = get_note_by_id(db, note_id, user_id)
    db.delete(note)
    db.commit()
    return True
