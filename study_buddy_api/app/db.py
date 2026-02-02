# app/db.py

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# A base class for ORM models is defined here.
# All database model classes are expected to inherit from this base.
class Base(DeclarativeBase):
    pass


# A SQLite database URL is defined here.
# A local file named study_buddy.db is expected to be created in the project root.
DATABASE_URL = "sqlite:///./study_buddy.db"


# A SQLAlchemy engine is created here.
# The check_same_thread flag is required for SQLite when used with FastAPI.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


# A session factory is created here.
# Sessions are expected to be created per request and closed after use.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
