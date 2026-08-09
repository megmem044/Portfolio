"""Handle viewing and safely managing spending categories."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.category import Category
from app.models.transaction import Transaction
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate


router = APIRouter(prefix="/categories", tags=["categories"])


def find_category(category_id: int, db: Session) -> Category:
    category = db.get(Category, category_id)
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


@router.get("/", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.name.asc()).all()


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
):
    category = Category(
        name=category_data.name,
        description=category_data.description,
        is_default=False,
    )
    db.add(category)
    commit_category(db)
    db.refresh(category)
    return category


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id: int, db: Session = Depends(get_db)):
    return find_category(category_id, db)


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    changes: CategoryUpdate,
    db: Session = Depends(get_db),
):
    category = find_category(category_id, db)
    if category.is_default:
        raise HTTPException(status_code=409, detail="default categories cannot be changed")

    for field, value in changes.model_dump(exclude_unset=True).items():
        setattr(category, field, value)

    commit_category(db)
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
) -> Response:
    category = find_category(category_id, db)
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

    db.delete(category)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
