# app/schemas/topic.py

from __future__ import annotations

from pydantic import BaseModel, Field


# A payload for creating a topic is defined here.
class TopicCreate(BaseModel):
    # A topic name is required here.
    name: str = Field(min_length=1, max_length=100)


# A payload for returning a topic is defined here.
class TopicRead(BaseModel):
    # A database id is returned here.
    id: int

    # A topic name is returned here.
    name: str

    # ORM mode is enabled here so SQLAlchemy objects can be returned directly.
    model_config = {"from_attributes": True}

