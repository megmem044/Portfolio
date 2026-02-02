# app/models/flashcard.py

from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


# A Flashcard table is defined here.
# Each flashcard is expected to belong to one topic.
class Flashcard(Base):
    # A table name is declared here for SQLite.
    __tablename__ = "flashcards"

    # A primary key column is defined here.
    id: Mapped[int] = mapped_column(primary_key=True)

    # A topic foreign key is defined here.
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"), index=True)

    # A front text field is defined here.
    front: Mapped[str] = mapped_column(String(200))

    # A back text field is defined here.
    back: Mapped[str] = mapped_column(Text())

    # A relationship back to topic is defined here.
    topic: Mapped["Topic"] = relationship(back_populates="flashcards")
