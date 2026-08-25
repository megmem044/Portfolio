"""Focused SQL analytics backed by grouped queries and window functions."""

from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import Integer, case, cast, extract, func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.analytics import CategorySummary, DataQualitySummary, LargestTransaction, MerchantSummary, MonthlyTrend

router = APIRouter(prefix="/analytics", tags=["analytics"])
CENT = Decimal("0.01")


@router.get("/monthly-trends", response_model=list[MonthlyTrend])
def monthly_trends(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    year = cast(extract("year", Transaction.date), Integer)
    month = cast(extract("month", Transaction.date), Integer)
    monthly = (
        select(year.label("year"), month.label("month"), func.count(Transaction.id).label("transaction_count"), func.sum(Transaction.amount).label("total"))
        .where(Transaction.owner_id == current_user.id)
        .group_by(year, month)
        .subquery()
    )
    ordering = (monthly.c.year, monthly.c.month)
    query = select(
        monthly,
        func.lag(monthly.c.total).over(order_by=ordering).label("previous_total"),
        func.avg(monthly.c.total).over(order_by=ordering, rows=(-2, 0)).label("rolling_average"),
    ).order_by(*ordering)
    results = []
    for row in db.execute(query).mappings():
        total = Decimal(row["total"]).quantize(CENT)
        previous = Decimal(row["previous_total"]).quantize(CENT) if row["previous_total"] is not None else None
        change = (total - previous).quantize(CENT) if previous is not None else None
        percentage = ((change / previous) * 100).quantize(CENT) if previous not in (None, Decimal("0.00")) else None
        results.append({"month": f"{row['year']:04d}-{row['month']:02d}", "transaction_count": row["transaction_count"], "total": total, "previous_total": previous, "absolute_change": change, "percentage_change": percentage, "three_month_rolling_average": Decimal(row["rolling_average"]).quantize(CENT)})
    return results


@router.get("/merchants", response_model=list[MerchantSummary])
def merchant_summaries(limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = db.execute(
        select(Transaction.merchant, func.count(Transaction.id).label("transaction_count"), func.sum(Transaction.amount).label("total"), func.avg(Transaction.amount).label("average_transaction"))
        .where(Transaction.owner_id == current_user.id)
        .group_by(Transaction.merchant)
        .order_by(func.sum(Transaction.amount).desc(), Transaction.merchant.asc())
        .limit(limit)
    ).mappings()
    return [{"merchant": row["merchant"], "transaction_count": row["transaction_count"], "total": Decimal(row["total"]).quantize(CENT), "average_transaction": Decimal(row["average_transaction"]).quantize(CENT)} for row in rows]


@router.get("/categories", response_model=list[CategorySummary])
def category_summaries(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    grand_total = select(func.sum(Transaction.amount)).where(Transaction.owner_id == current_user.id).scalar_subquery()
    rows = db.execute(
        select(Category.name.label("category"), func.count(Transaction.id).label("transaction_count"), func.sum(Transaction.amount).label("total"), (func.sum(Transaction.amount) * 100 / func.nullif(grand_total, 0)).label("share_percent"))
        .join(Transaction, Transaction.category_id == Category.id)
        .where(Transaction.owner_id == current_user.id)
        .group_by(Category.name)
        .order_by(func.sum(Transaction.amount).desc(), Category.name.asc())
    ).mappings()
    return [{"category": row["category"], "transaction_count": row["transaction_count"], "total": Decimal(row["total"]).quantize(CENT), "share_percent": Decimal(row["share_percent"]).quantize(CENT)} for row in rows]


@router.get("/largest-transactions", response_model=list[LargestTransaction])
def largest_transactions(limit: int = Query(default=10, ge=1, le=100), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = db.execute(select(Transaction.id, Transaction.date, Transaction.merchant, Category.name.label("category"), Transaction.amount).join(Category, Transaction.category_id == Category.id).where(Transaction.owner_id == current_user.id).order_by(Transaction.amount.desc(), Transaction.date.desc(), Transaction.id.desc()).limit(limit)).mappings()
    return [{"id": row["id"], "date": row["date"].isoformat(), "merchant": row["merchant"], "category": row["category"], "amount": Decimal(row["amount"]).quantize(CENT)} for row in rows]


@router.get("/data-quality", response_model=DataQualitySummary)
def data_quality(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total, uncategorized = db.execute(select(func.count(Transaction.id), func.sum(case((Category.name == "Uncategorized", 1), else_=0))).join(Category, Transaction.category_id == Category.id).where(Transaction.owner_id == current_user.id)).one()
    total = int(total or 0); uncategorized = int(uncategorized or 0)
    rate = ((Decimal(uncategorized) / Decimal(total)) * 100).quantize(CENT) if total else Decimal("0.00")
    return {"transaction_count": total, "uncategorized_count": uncategorized, "uncategorized_rate": rate}
