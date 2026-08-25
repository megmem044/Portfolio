"""Describe how transaction records and their category link are stored."""

from sqlalchemy import Column, Date, ForeignKey, Index, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base

# Transaction table definition is declared
# Each class attribute maps to a database column
class Transaction(Base):
    # Table name is defined
    __tablename__ = "transactions"
    __table_args__ = (
        UniqueConstraint("owner_id", "fingerprint", name="uq_transaction_owner_fingerprint"),
        Index("ix_transactions_owner_date", "owner_id", "date"),
        Index("ix_transactions_owner_merchant", "owner_id", "merchant"),
    )

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
    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # Transaction date is stored
    date = Column(Date, nullable=False, index=True)
    fingerprint = Column(String(64), nullable=True, index=True)

    category_record = relationship("Category", back_populates="transactions")
    owner = relationship("User", back_populates="transactions")
    source_row = relationship("TransactionImportRow", back_populates="transaction", uselist=False)

    @property
    def category(self) -> str:
        return self.category_record.name
