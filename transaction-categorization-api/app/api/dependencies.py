from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Give one database session to a request and close it afterward."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
