# app/deps.py

from __future__ import annotations

from typing import Generator

from sqlalchemy.orm import Session

from app.db import SessionLocal


# A database session dependency is defined here.
# A new session is created per request and closed after use.
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
