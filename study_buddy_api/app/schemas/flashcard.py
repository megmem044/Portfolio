# app/schemas/flashcard.py

from __future__ import annotations

from pydantic import BaseModel, Field


# A payload for creating a flashcard is defined here.
class FlashcardCreate(BaseModel):
    # A topic id is required here.
    topic_id: int

    # A front side is required here.
    front: str = Field(min_length=1, max_length=200)

    # A back side is required here.
    back: str = Field(min_length=1)


# A payload for returning a flashcard is defined here.
class FlashcardRead(BaseModel):
    # A database id is returned here.
    id: int

    # A topic id is returned here.
    topic_id: int

    # A front side is returned here.
    front: str

    # A back side is returned here.
    back: str

    # ORM mode is enabled here so SQLAlchemy objects can be returned directly.
    model_config = {"from_attributes": True}
