from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.transaction import Transaction
from app.schemas.transaction import MonthlySummary, TransactionCreate, TransactionRead
from app.services.categorizer import categorize_transaction

# Router object is created for transaction related endpoints
router = APIRouter(prefix="/transactions", tags=["transactions"])


# Database session dependency is defined
def get_db():
    # Database session is created
    db = SessionLocal()
    try:
        # Session is yielded to the request
        yield db
    finally:
        # Session is closed after request completion
        db.close()


# Transaction creation endpoint is defined
@router.post("/", response_model=TransactionRead)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
):
    # Category is determined using business logic
    category = categorize_transaction(transaction.merchant)

    # Transaction database object is created
    db_transaction = Transaction(
        amount=transaction.amount,
        merchant=transaction.merchant,
        category=category,
        date=transaction.date,
    )

    # Transaction is added to the database session
    db.add(db_transaction)

    # Changes are committed to the database
    db.commit()

    # Database generated values are refreshed
    db.refresh(db_transaction)

    # Stored transaction is returned
    return db_transaction


# Transaction list endpoint is defined
@router.get("/", response_model=list[TransactionRead])
def list_transactions(
    start: date | None = None,
    end: date | None = None,
    db: Session = Depends(get_db),
):
    # Base query for transactions is created
    query = db.query(Transaction)

    # Start date filter is applied if provided
    if start is not None:
        query = query.filter(Transaction.date >= start)

    # End date filter is applied if provided
    if end is not None:
        query = query.filter(Transaction.date <= end)

    # Query results are returned
    return query.all()


# Monthly summary endpoint is defined
@router.get("/summary", response_model=MonthlySummary)
def monthly_summary(
    month: str,
    db: Session = Depends(get_db),
):
    # Month value is expected in YYYY MM form
    month_key = month

    # Month extraction expression is defined for SQLite
    month_expr = func.strftime("%Y-%m", Transaction.date)

    # Grouped totals are computed at the database level
    grouped_rows = (
        db.query(
            Transaction.category.label("category"),
            func.count(Transaction.id).label("transaction_count"),
            func.sum(Transaction.amount).label("category_total"),
        )
        .filter(month_expr == month_key)
        .group_by(Transaction.category)
        .all()
    )

    # Totals by category container is created
    totals_by_category: dict[str, float] = {}

    # Overall total accumulator is created
    overall_total = 0.0

    # Transaction count accumulator is created
    transaction_count = 0

    # Grouped rows are converted into the response structures
    for row in grouped_rows:
        # Category label is read
        category = row.category

        # Category total value is normalized
        category_total = float(row.category_total or 0.0)

        # Transaction count value is normalized
        category_count = int(row.transaction_count or 0)

        # Category total is stored
        totals_by_category[category] = category_total

        # Overall total is accumulated
        overall_total += category_total

        # Overall transaction count is accumulated
        transaction_count += category_count

    # Summary response is returned
    return {
        "month": month_key,
        "transaction_count": transaction_count,
        "overall_total": overall_total,
        "totals_by_category": totals_by_category,
    }
