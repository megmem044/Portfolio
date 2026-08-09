from __future__ import annotations

from datetime import date as Date
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Schema for creating a transaction is defined
# This schema validates incoming request data
class TransactionCreate(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    merchant: str = Field(min_length=1, max_length=200)
    date: Date

    @field_validator("merchant")
    @classmethod
    def clean_merchant(cls, merchant: str) -> str:
        cleaned = merchant.strip()
        if not cleaned:
            raise ValueError("merchant must not be blank")
        return cleaned


# Schema for returning a transaction is defined
# This schema controls response formatting
class TransactionUpdate(BaseModel):
    amount: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    merchant: str | None = Field(default=None, min_length=1, max_length=200)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    date: Date | None = None

    @field_validator("merchant", "category")
    @classmethod
    def clean_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("value must not be blank")
        return cleaned

    @model_validator(mode="after")
    def require_a_change(self):
        if not self.model_fields_set:
            raise ValueError("at least one field must be provided")
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("updated fields cannot be null")
        return self


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    merchant: str
    category: str
    date: Date

# Schema for monthly summary response is defined
class TransactionSortField(str, Enum):
    date = "date"
    amount = "amount"
    merchant = "merchant"
    category = "category"


class SortDirection(str, Enum):
    asc = "asc"
    desc = "desc"


class TransactionPage(BaseModel):
    items: list[TransactionRead]
    total: int
    page: int
    page_size: int


class MonthlySummary(BaseModel):
    # Month string is returned
    month: str

    # Transaction count is returned
    transaction_count: int

    overall_total: Decimal

    # Totals by category are returned
    totals_by_category: dict[str, Decimal]

