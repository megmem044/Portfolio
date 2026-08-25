"""API contracts for staged CSV imports."""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ImportMapping(BaseModel):
    date: str = "date"
    merchant: str = "merchant"
    amount: str | None = "amount"
    debit: str | None = None
    credit: str | None = None
    currency: str | None = "currency"


class ImportCreate(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    source: str = Field(default="csv", min_length=1, max_length=100)
    csv_content: str = Field(min_length=1)
    mapping: ImportMapping = Field(default_factory=ImportMapping)


class ImportRowRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    row_number: int
    raw_values: dict
    merchant_raw: str | None
    merchant: str | None
    amount: Decimal | None
    date: date | None
    currency: str | None
    fingerprint: str | None
    status: str
    error_reason: str | None
    transaction_id: int | None
    review_decision: str | None


class ImportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    filename: str
    source: str
    state: str
    input_count: int
    imported_count: int
    duplicate_count: int
    invalid_count: int
    rejected_count: int
    created_at: datetime
    committed_at: datetime | None
    parsing_ms: int
    validation_ms: int
    staging_ms: int
    commit_ms: int
    rows_per_second: Decimal
    peak_memory_bytes: int | None
    rows: list[ImportRowRead]
    row_total: int
    page: int
    page_size: int


class ImportCommit(BaseModel):
    possible_duplicates: Literal["import", "reject"] = "reject"


class ImportRowDecision(BaseModel):
    decision: Literal["approve", "reject"]


class ImportPreset(BaseModel):
    id: str
    name: str
    mapping: ImportMapping


class ReconciliationRead(BaseModel):
    import_id: int
    state: str
    input_count: int
    imported_count: int
    duplicate_count: int
    invalid_count: int
    rejected_count: int
    accounted_count: int
    reconciled: bool
    accepted_total: Decimal
    saved_total: Decimal
