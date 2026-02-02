# app/models/topic.py

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from typing import List
from sqlalchemy.orm import relationship

from app.db import Base


# A Topic table is defined here.
# A topic is expected to be a named container for flashcards.
class Topic(Base):
    # A table name is declared here for SQLite.
    __tablename__ = "topics"

    # A primary key column is defined here.
    id: Mapped[int] = mapped_column(primary_key=True)

    # A name column is defined here.
    # A unique constraint is avoided for now to keep early steps simple.
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    
    # A one-to-many relationship to flashcards is defined here.
    flashcards: Mapped[List["Flashcard"]] = relationship(back_populates="topic")
