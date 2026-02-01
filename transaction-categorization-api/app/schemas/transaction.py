from datetime import date
from pydantic import BaseModel

# Schema for creating a transaction is defined
# This schema validates incoming request data
class TransactionCreate(BaseModel):
    # Transaction amount is provided
    amount: float

    # Merchant name is provided
    merchant: str

    # Transaction date is provided
    date: date


# Schema for returning a transaction is defined
# This schema controls response formatting
class TransactionRead(BaseModel):
    # Unique identifier is returned
    id: int

    # Transaction amount is returned
    amount: float

    # Merchant name is returned
    merchant: str

    # Category label is returned
    category: str

    # Transaction date is returned
    date: date

    class Config:
       
         from_attributes = True

# Schema for monthly summary response is defined
class MonthlySummary(BaseModel):
    # Month string is returned
    month: str

    # Transaction count is returned
    transaction_count: int

    # Overall total is returned
    overall_total: float

    # Totals by category are returned
    totals_by_category: dict[str, float]

