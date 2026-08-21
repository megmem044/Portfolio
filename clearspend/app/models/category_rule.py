"""Describe merchant keywords that automatically select a category."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base


class CategoryRule(Base):
    __tablename__ = "category_rules"
    __table_args__ = (
        UniqueConstraint("owner_id", "keyword", name="uq_category_rules_owner_keyword"),
    )

    id = Column(Integer, primary_key=True)
    keyword = Column(String(100), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    priority = Column(Integer, nullable=False, default=100, index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    is_default = Column(Boolean, nullable=False, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    category = relationship("Category", back_populates="rules")
    owner = relationship("User", back_populates="category_rules")

    @property
    def category_name(self) -> str:
        return self.category.name
