"""Response contracts for focused SQL analytics."""

from decimal import Decimal

from pydantic import BaseModel


class MonthlyTrend(BaseModel):
    month: str
    transaction_count: int
    total: Decimal
    previous_total: Decimal | None
    absolute_change: Decimal | None
    percentage_change: Decimal | None
    three_month_rolling_average: Decimal


class MerchantSummary(BaseModel):
    merchant: str
    transaction_count: int
    total: Decimal
    average_transaction: Decimal


class CategorySummary(BaseModel):
    category: str
    transaction_count: int
    total: Decimal
    share_percent: Decimal


class LargestTransaction(BaseModel):
    id: int
    date: str
    merchant: str
    category: str
    amount: Decimal


class DataQualitySummary(BaseModel):
    transaction_count: int
    uncategorized_count: int
    uncategorized_rate: Decimal
