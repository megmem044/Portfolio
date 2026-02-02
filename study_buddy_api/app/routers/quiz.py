# app/routers/quiz.py

from __future__ import annotations

import random
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models.flashcard import Flashcard
from app.models.topic import Topic
from app.schemas.flashcard import FlashcardRead


# A router for quiz endpoints is defined here.
router = APIRouter(
    prefix="/topics",
    tags=["quiz"],
)


# A quiz endpoint is defined here.
@router.get(
    "/{topic_id}/quiz",
    response_model=List[FlashcardRead],
)
def quiz_for_topic(
    topic_id: int,
    count: int = Query(default=5, ge=1, le=50),
    db: Session = Depends(get_db),
) -> List[Flashcard]:
    # The topic existence is checked here.
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="topic not found",
        )

    # All flashcards for the topic are loaded here.
    flashcards = db.query(Flashcard).filter(Flashcard.topic_id == topic_id).all()

    # An empty topic is handled here.
    if len(flashcards) == 0:
        return []

    # A random sample is returned here.
    # If count exceeds the available cards, all cards are shuffled and returned.
    if count >= len(flashcards):
        random.shuffle(flashcards)
        return flashcards

    return random.sample(flashcards, k=count)
