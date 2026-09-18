import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class NoteCategory(str, enum.Enum):
    TRANSLATION = "translation"
    GRAMMAR = "grammar"
    SYNONYM = "synonym"
    VOCABULARY = "vocabulary"
    PHRASE = "phrase"
    OTHER = "other"


class Note(Base):
    __tablename__ = "notes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    title = Column(String(255), nullable=False)
    original_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=True)

    source_language = Column(String(10), default="en")
    target_language = Column(String(10), nullable=True)

    category = Column(Enum(NoteCategory), default=NoteCategory.OTHER)
    tags = Column(String, nullable=True)          # comma-separated tags

    audio_file_path = Column(String, nullable=True)   # path to stored voice message

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    owner = relationship("User", back_populates="notes")
