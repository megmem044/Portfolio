# app/routers/topic.py

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models.flashcard import Flashcard
from app.models.topic import Topic
from app.schemas.flashcard import FlashcardRead
from app.schemas.topic import TopicCreate, TopicRead



# A router for topic-related endpoints is defined here.
router = APIRouter(
    prefix="/topics",
    tags=["topics"],
)


# A topic creation endpoint is defined here.
@router.post(
    "",
    response_model=TopicRead,
    status_code=status.HTTP_201_CREATED,
)
def create_topic(
    payload: TopicCreate,
    db: Session = Depends(get_db),
) -> Topic:
    
    existing = db.query(Topic).filter(Topic.name == payload.name).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="topic already exists",
        )

    # A Topic ORM object is created here from the request payload.
    topic = Topic(name=payload.name)

    # The object is added to the database session here.
    db.add(topic)

    # The transaction is committed here.
    db.commit()

    # The object is refreshed so generated fields are available.
    db.refresh(topic)

    return topic

# A topic listing endpoint is defined here.
@router.get(
    "",
    response_model=List[TopicRead],
)
def list_topics(
    db: Session = Depends(get_db),
) -> List[Topic]:
    # All topics are selected here.
    topics = db.query(Topic).order_by(Topic.id.asc()).all()
    return topics

# A topic-scoped flashcard listing endpoint is defined here.
@router.get(
    "/{topic_id}/flashcards",
    response_model=List[FlashcardRead],
)
def list_flashcards_for_topic(
    topic_id: int,
    db: Session = Depends(get_db),
) -> List[Flashcard]:
    # The topic existence is checked here.
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="topic not found",
        )

    # Flashcards for the topic are selected here.
    flashcards = (
        db.query(Flashcard)
        .filter(Flashcard.topic_id == topic_id)
        .order_by(Flashcard.id.asc())
        .all()
    )
    return flashcards
