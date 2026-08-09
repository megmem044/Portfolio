"""Describe how transaction records and their category link are stored."""

from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.db.base import Base

# Transaction table definition is declared
# Each class attribute maps to a database column
class Transaction(Base):
    # Table name is defined
    __tablename__ = "transactions"

    # Primary key column is defined
    id = Column(Integer, primary_key=True, index=True)

    # Numeric avoids the rounding errors that floating-point money can cause.
    amount = Column(Numeric(12, 2), nullable=False)

    # Merchant name is stored
    merchant = Column(String(200), nullable=False)

    # Category label is stored
    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False,
        index=True,
    )

    # Transaction date is stored
    date = Column(Date, nullable=False, index=True)

    category_record = relationship("Category", back_populates="transactions")

    @property
    def category(self) -> str:
        return self.category_record.name
