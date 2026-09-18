from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.models.note import NoteCategory


class NoteCreate(BaseModel):
    title: str
    original_text: str
    translated_text: Optional[str] = None
    source_language: str = "en"
    target_language: Optional[str] = None
    category: NoteCategory = NoteCategory.OTHER
    tags: Optional[str] = None


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    original_text: Optional[str] = None
    translated_text: Optional[str] = None
    target_language: Optional[str] = None
    category: Optional[NoteCategory] = None
    tags: Optional[str] = None


class NoteResponse(BaseModel):
    id: str
    user_id: str
    title: str
    original_text: str
    translated_text: Optional[str]
    source_language: str
    target_language: Optional[str]
    category: NoteCategory
    tags: Optional[str]
    audio_file_path: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NoteListResponse(BaseModel):
    notes: List[NoteResponse]
    total: int
