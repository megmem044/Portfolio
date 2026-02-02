# app/routers/flashcard.py

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models.flashcard import Flashcard
from app.models.topic import Topic
from app.schemas.flashcard import FlashcardCreate, FlashcardRead


# A router for flashcard-related endpoints is defined here.
router = APIRouter(
    prefix="/flashcards",
    tags=["flashcards"],
)


# A flashcard creation endpoint is defined here.
@router.post(
    "",
    response_model=FlashcardRead,
    status_code=status.HTTP_201_CREATED,
)
def create_flashcard(
    payload: FlashcardCreate,
    db: Session = Depends(get_db),
) -> Flashcard:
    # The topic is validated here so orphan flashcards are avoided.
    topic = db.query(Topic).filter(Topic.id == payload.topic_id).first()
    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="topic not found",
        )

    # A Flashcard ORM object is created here.
    flashcard = Flashcard(
        topic_id=payload.topic_id,
        front=payload.front,
        back=payload.back,
    )

    # The object is persisted here.
    db.add(flashcard)
    db.commit()
    db.refresh(flashcard)

    return flashcard


# A flashcard listing endpoint is defined here.
@router.get(
    "",
    response_model=List[FlashcardRead],
)
def list_flashcards(
    db: Session = Depends(get_db),
) -> List[Flashcard]:
    # All flashcards are selected here.
    flashcards = db.query(Flashcard).order_by(Flashcard.id.asc()).all()
    return flashcards
