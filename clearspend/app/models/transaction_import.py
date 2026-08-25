"""Staging and lineage records for transaction-file imports."""

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class TransactionImport(Base):
    __tablename__ = "transaction_imports"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    source = Column(String(100), nullable=False)
    state = Column(String(20), nullable=False, default="ready", index=True)
    file_hash = Column(String(64), nullable=False)
    input_count = Column(Integer, nullable=False, default=0)
    imported_count = Column(Integer, nullable=False, default=0)
    duplicate_count = Column(Integer, nullable=False, default=0)
    invalid_count = Column(Integer, nullable=False, default=0)
    rejected_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    committed_at = Column(DateTime(timezone=True), nullable=True)
    parsing_ms = Column(Integer, nullable=False, default=0)
    validation_ms = Column(Integer, nullable=False, default=0)
    staging_ms = Column(Integer, nullable=False, default=0)
    commit_ms = Column(Integer, nullable=False, default=0)
    rows_per_second = Column(Numeric(12, 2), nullable=False, default=0)
    peak_memory_bytes = Column(Integer, nullable=True)

    owner = relationship("User", back_populates="transaction_imports")
    rows = relationship("TransactionImportRow", back_populates="transaction_import", cascade="all, delete-orphan", order_by="TransactionImportRow.row_number")


class TransactionImportRow(Base):
    __tablename__ = "transaction_import_rows"
    __table_args__ = (UniqueConstraint("import_id", "row_number", name="uq_import_row_number"),)

    id = Column(Integer, primary_key=True)
    import_id = Column(Integer, ForeignKey("transaction_imports.id"), nullable=False, index=True)
    row_number = Column(Integer, nullable=False)
    raw_values = Column(JSON, nullable=False)
    merchant_raw = Column(String(500), nullable=True)
    merchant = Column(String(200), nullable=True)
    amount = Column(Numeric(12, 2), nullable=True)
    date = Column(Date, nullable=True)
    currency = Column(String(3), nullable=True)
    fingerprint = Column(String(64), nullable=True, index=True)
    status = Column(String(30), nullable=False, index=True)
    error_reason = Column(Text, nullable=True)
    review_decision = Column(String(20), nullable=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True, unique=True)

    transaction_import = relationship("TransactionImport", back_populates="rows")
    transaction = relationship("Transaction", back_populates="source_row")
