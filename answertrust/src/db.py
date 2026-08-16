"""SQLAlchemy connection and session helpers."""

from collections.abc import Iterator
from contextlib import contextmanager
import os

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.config import PROJECT_ROOT


DEFAULT_DATABASE_URL = f"sqlite:///{(PROJECT_ROOT / 'data' / 'answertrust-v2.db').as_posix()}"


def database_url() -> str:
    """Use DATABASE_URL when provided, otherwise use a local development file."""
    url = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def create_database_engine(url: str | None = None) -> Engine:
    """Create an engine for PostgreSQL or the local SQLite fallback."""
    selected_url = url or database_url()
    options = {"check_same_thread": False} if selected_url.startswith("sqlite") else {}
    return create_engine(selected_url, pool_pre_ping=True, connect_args=options)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create new database sessions without expiring returned objects."""
    return sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def session_scope(factory: sessionmaker[Session]) -> Iterator[Session]:
    """Save successful work and undo work when an error occurs."""
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
