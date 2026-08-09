from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Schema for creating a transaction is defined
# This schema validates incoming request data
class TransactionCreate(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    merchant: str = Field(min_length=1, max_length=200)
    date: date

    @field_validator("merchant")
    @classmethod
    def clean_merchant(cls, merchant: str) -> str:
        cleaned = merchant.strip()
        if not cleaned:
            raise ValueError("merchant must not be blank")
        return cleaned


# Schema for returning a transaction is defined
# This schema controls response formatting
class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    merchant: str
    category: str
    date: date

# Schema for monthly summary response is defined
class MonthlySummary(BaseModel):
    # Month string is returned
    month: str

    # Transaction count is returned
    transaction_count: int

    overall_total: Decimal

    # Totals by category are returned
    totals_by_category: dict[str, Decimal]

