from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Database engine is created using the configured database URL
# The engine manages connections to the database file
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}
)

# Session factory is created
# Each session represents a single database conversation
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
