"""Handle viewing and safely managing spending categories."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.category import Category
from app.models.category_rule import CategoryRule
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate


router = APIRouter(prefix="/categories", tags=["categories"])


def find_category(category_id: int, owner_id: int, db: Session) -> Category:
    category = (
        db.query(Category)
        .filter(
            Category.id == category_id,
            or_(Category.is_default.is_(True), Category.owner_id == owner_id),
        )
        .one_or_none()
    )
    if category is None:
        raise HTTPException(status_code=404, detail="category not found")
    return category


def commit_category(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="category name already exists",
        ) from error


def category_name_exists(
    name: str,
    owner_id: int,
    db: Session,
    exclude_id: int | None = None,
) -> bool:
    query = db.query(Category.id).filter(
        Category.name == name,
        or_(Category.is_default.is_(True), Category.owner_id == owner_id),
    )
    if exclude_id is not None:
        query = query.filter(Category.id != exclude_id)
    return query.first() is not None


@router.get("/", response_model=list[CategoryRead])
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Category)
        .filter(
            or_(Category.is_default.is_(True), Category.owner_id == current_user.id)
        )
        .order_by(Category.name.asc())
        .all()
    )


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if category_name_exists(category_data.name, current_user.id, db):
        raise HTTPException(status_code=409, detail="category name already exists")

    category = Category(
        name=category_data.name,
        description=category_data.description,
        is_default=False,
        owner=current_user,
    )
    db.add(category)
    commit_category(db)
    db.refresh(category)
    return category


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return find_category(category_id, current_user.id, db)


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    changes: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = find_category(category_id, current_user.id, db)
    if category.is_default:
        raise HTTPException(status_code=409, detail="default categories cannot be changed")

    if (
        changes.name is not None
        and category_name_exists(
            changes.name,
            current_user.id,
            db,
            exclude_id=category.id,
        )
    ):
        raise HTTPException(status_code=409, detail="category name already exists")

    for field, value in changes.model_dump(exclude_unset=True).items():
        setattr(category, field, value)

    commit_category(db)
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    category = find_category(category_id, current_user.id, db)
    if category.is_default:
        raise HTTPException(status_code=409, detail="default categories cannot be deleted")

    is_in_use = (
        db.query(Transaction.id)
        .filter(Transaction.category_id == category.id)
        .first()
        is not None
    )
    if is_in_use:
        raise HTTPException(status_code=409, detail="category is used by transactions")

    has_rules = (
        db.query(CategoryRule.id)
        .filter(CategoryRule.category_id == category.id)
        .first()
        is not None
    )
    if has_rules:
        raise HTTPException(status_code=409, detail="category is used by rules")

    db.delete(category)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
