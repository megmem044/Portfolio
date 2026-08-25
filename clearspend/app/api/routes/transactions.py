"""Handle transaction creation, browsing, reports, updates, and deletion."""

from datetime import date
from decimal import Decimal
import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.category import Category
from app.models.category_rule import CategoryRule
from app.models.transaction import Transaction
from app.models.user import User
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


def find_category(name: str, owner_id: int, db: Session) -> Category:
    category = (
        db.query(Category)
        .filter(
            Category.name == name,
            or_(Category.is_default.is_(True), Category.owner_id == owner_id),
        )
        .one_or_none()
    )
    if category is None:
        raise HTTPException(status_code=422, detail="category does not exist")
    return category


def categorize_merchant(merchant: str, owner_id: int, db: Session) -> str:
    stored_rules = (
        db.query(CategoryRule)
        .join(CategoryRule.category)
        .filter(
            CategoryRule.is_active.is_(True),
            or_(
                CategoryRule.is_default.is_(True),
                CategoryRule.owner_id == owner_id,
            ),
        )
        .order_by(CategoryRule.priority.asc(), CategoryRule.id.asc())
        .all()
    )
    rules = ((rule.keyword, rule.category.name) for rule in stored_rules)
    return categorize_transaction(merchant, rules)


# Transaction creation endpoint is defined
@router.post("/", response_model=TransactionRead)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Category is determined using business logic
    category_name = categorize_merchant(transaction.merchant, current_user.id, db)
    category = find_category(category_name, current_user.id, db)

    # Transaction database object is created
    db_transaction = Transaction(
        amount=transaction.amount,
        merchant=transaction.merchant,
        category_record=category,
        owner=current_user,
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
    current_user: User = Depends(get_current_user),
):
    if start is not None and end is not None and start > end:
        raise HTTPException(
            status_code=422,
            detail="start date must be on or before end date",
        )

    # Base query for transactions is created
    query = (
        db.query(Transaction)
        .join(Transaction.category_record)
        .filter(Transaction.owner_id == current_user.id)
    )

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
    current_user: User = Depends(get_current_user),
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
            Transaction.owner_id == current_user.id,
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


@router.get("/export.csv")
def export_transactions(
    start: date | None = None,
    end: date | None = None,
    category: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if start is not None and end is not None and start > end:
        raise HTTPException(status_code=422, detail="start date must be on or before end date")
    query = db.query(Transaction).join(Transaction.category_record).filter(Transaction.owner_id == current_user.id)
    if start is not None: query = query.filter(Transaction.date >= start)
    if end is not None: query = query.filter(Transaction.date <= end)
    if category: query = query.filter(Category.name == category.strip())
    if search: query = query.filter(Transaction.merchant.ilike(f"%{search.strip()}%"))
    output = io.StringIO(); writer = csv.writer(output, lineterminator="\n"); writer.writerow(["date", "merchant", "category", "amount"])
    for transaction in query.order_by(Transaction.date.desc(), Transaction.id.desc()).yield_per(1000):
        writer.writerow([transaction.date.isoformat(), transaction.merchant, transaction.category, f"{Decimal(transaction.amount):.2f}"])
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=clearspend-transactions.csv"})


def find_transaction(
    transaction_id: int,
    owner_id: int,
    db: Session,
) -> Transaction:
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.owner_id == owner_id,
        )
        .one_or_none()
    )
    if transaction is None:
        raise HTTPException(status_code=404, detail="transaction not found")
    return transaction


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return find_transaction(transaction_id, current_user.id, db)


@router.patch("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: int,
    changes: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = find_transaction(transaction_id, current_user.id, db)
    update_data = changes.model_dump(exclude_unset=True)
    requested_category = update_data.pop("category", None)

    for field, value in update_data.items():
        setattr(transaction, field, value)

    if requested_category is not None:
        transaction.category_record = find_category(
            requested_category,
            current_user.id,
            db,
        )
    elif "merchant" in update_data:
        category_name = categorize_merchant(
            transaction.merchant,
            current_user.id,
            db,
        )
        transaction.category_record = find_category(
            category_name,
            current_user.id,
            db,
        )

    db.commit()
    db.refresh(transaction)
    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    transaction = find_transaction(transaction_id, current_user.id, db)
    db.delete(transaction)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
