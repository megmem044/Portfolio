"""Describe how default and user-created spending categories are stored."""

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(String(300), nullable=True)
    is_default = Column(Boolean, nullable=False, default=False)

    transactions = relationship("Transaction", back_populates="category_record")
    rules = relationship("CategoryRule", back_populates="category")
