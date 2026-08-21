"""Provide the shared base class used by all database models."""

from sqlalchemy.orm import declarative_base

# Base class for all SQLAlchemy models is created
# All database table classes will inherit from this base
Base = declarative_base()

