from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.category import Category
from app.models.transaction import Transaction
from app.schemas.transaction import (
    MonthlySummary,
    SortDirection,
    TransactionCreate,
    TransactionPage,
    TransactionRead,
    TransactionSortField,
    TransactionUpdate,
)
from app.services.categorizer import categorize_transaction

# Router object is created for transaction related endpoints
router = APIRouter(prefix="/transactions", tags=["transactions"])


def find_category(name: str, db: Session) -> Category:
    category = db.query(Category).filter(Category.name == name).one_or_none()
    if category is None:
        raise HTTPException(status_code=422, detail="category does not exist")
    return category


# Transaction creation endpoint is defined
@router.post("/", response_model=TransactionRead)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
):
    # Category is determined using business logic
    category_name = categorize_transaction(transaction.merchant)
    category = find_category(category_name, db)

    # Transaction database object is created
    db_transaction = Transaction(
        amount=transaction.amount,
        merchant=transaction.merchant,
        category_record=category,
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
@router.get("/", response_model=TransactionPage)
def list_transactions(
    start: date | None = None,
    end: date | None = None,
    category: str | None = Query(default=None, min_length=1, max_length=100),
    search: str | None = Query(default=None, min_length=1, max_length=200),
    sort_by: TransactionSortField = TransactionSortField.date,
    sort_direction: SortDirection = SortDirection.desc,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    if start is not None and end is not None and start > end:
        raise HTTPException(
            status_code=422,
            detail="start date must be on or before end date",
        )

    # Base query for transactions is created
    query = db.query(Transaction).join(Transaction.category_record)

    # Start date filter is applied if provided
    if start is not None:
        query = query.filter(Transaction.date >= start)

    # End date filter is applied if provided
    if end is not None:
        query = query.filter(Transaction.date <= end)

    if category is not None:
        query = query.filter(Category.name == category.strip())

    if search is not None:
        query = query.filter(Transaction.merchant.ilike(f"%{search.strip()}%"))

    total = query.count()
    sort_column = getattr(Transaction, sort_by.value)
    order_expression = (
        sort_column.asc()
        if sort_direction == SortDirection.asc
        else sort_column.desc()
    )
    items = (
        query.order_by(order_expression, Transaction.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


# Monthly summary endpoint is defined
@router.get("/summary", response_model=MonthlySummary)
def monthly_summary(
    month: str = Query(pattern=r"^\d{4}-(0[1-9]|1[0-2])$"),
    db: Session = Depends(get_db),
):
    month_key = month
    year, month_number = (int(part) for part in month_key.split("-"))
    month_start = date(year, month_number, 1)
    next_month = (
        date(year + 1, 1, 1)
        if month_number == 12
        else date(year, month_number + 1, 1)
    )

    # Grouped totals are computed at the database level
    grouped_rows = (
        db.query(
            Category.name.label("category"),
            func.count(Transaction.id).label("transaction_count"),
            func.sum(Transaction.amount).label("category_total"),
        )
        .join(Transaction.category_record)
        .filter(
            Transaction.date >= month_start,
            Transaction.date < next_month,
        )
        .group_by(Category.name)
        .all()
    )

    # Totals by category container is created
    totals_by_category: dict[str, Decimal] = {}

    # Overall total accumulator is created
    overall_total = Decimal("0.00")

    # Transaction count accumulator is created
    transaction_count = 0

    # Grouped rows are converted into the response structures
    for row in grouped_rows:
        # Category label is read
        category = row.category

        category_total = Decimal(row.category_total or 0).quantize(Decimal("0.01"))

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


def find_transaction(transaction_id: int, db: Session) -> Transaction:
    transaction = db.get(Transaction, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="transaction not found")
    return transaction


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
):
    return find_transaction(transaction_id, db)


@router.patch("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: int,
    changes: TransactionUpdate,
    db: Session = Depends(get_db),
):
    transaction = find_transaction(transaction_id, db)
    update_data = changes.model_dump(exclude_unset=True)
    requested_category = update_data.pop("category", None)

    for field, value in update_data.items():
        setattr(transaction, field, value)

    if requested_category is not None:
        transaction.category_record = find_category(requested_category, db)
    elif "merchant" in update_data:
        category_name = categorize_transaction(transaction.merchant)
        transaction.category_record = find_category(category_name, db)

    db.commit()
    db.refresh(transaction)
    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
) -> Response:
    transaction = find_transaction(transaction_id, db)
    db.delete(transaction)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
