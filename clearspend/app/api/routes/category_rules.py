"""Handle viewing and managing automatic merchant-category rules."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.category import Category
from app.models.category_rule import CategoryRule
from app.models.user import User
from app.schemas.category_rule import (
    CategoryRuleCreate,
    CategoryRuleRead,
    CategoryRuleUpdate,
)


router = APIRouter(prefix="/rules", tags=["category rules"])


def find_rule(rule_id: int, owner_id: int, db: Session) -> CategoryRule:
    rule = (
        db.query(CategoryRule)
        .filter(
            CategoryRule.id == rule_id,
            or_(CategoryRule.is_default.is_(True), CategoryRule.owner_id == owner_id),
        )
        .one_or_none()
    )
    if rule is None:
        raise HTTPException(status_code=404, detail="category rule not found")
    return rule


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
        raise HTTPException(status_code=422, detail="category does not exist")
    return category


def commit_rule(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="rule keyword already exists",
        ) from error


@router.get("/", response_model=list[CategoryRuleRead])
def list_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(CategoryRule)
        .join(CategoryRule.category)
        .filter(
            or_(
                CategoryRule.is_default.is_(True),
                CategoryRule.owner_id == current_user.id,
            )
        )
        .order_by(CategoryRule.priority.asc(), CategoryRule.id.asc())
        .all()
    )


@router.post("/", response_model=CategoryRuleRead, status_code=status.HTTP_201_CREATED)
def create_rule(
    rule_data: CategoryRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = find_category(rule_data.category_id, current_user.id, db)
    rule = CategoryRule(
        keyword=rule_data.keyword,
        category=category,
        priority=rule_data.priority,
        is_active=rule_data.is_active,
        is_default=False,
        owner=current_user,
    )
    db.add(rule)
    commit_rule(db)
    db.refresh(rule)
    return rule


@router.get("/{rule_id}", response_model=CategoryRuleRead)
def get_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return find_rule(rule_id, current_user.id, db)


@router.patch("/{rule_id}", response_model=CategoryRuleRead)
def update_rule(
    rule_id: int,
    changes: CategoryRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rule = find_rule(rule_id, current_user.id, db)
    if rule.is_default:
        raise HTTPException(status_code=409, detail="default rules cannot be changed")
    update_data = changes.model_dump(exclude_unset=True)
    requested_category_id = update_data.pop("category_id", None)

    for field, value in update_data.items():
        setattr(rule, field, value)

    if requested_category_id is not None:
        rule.category = find_category(requested_category_id, current_user.id, db)

    commit_rule(db)
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    rule = find_rule(rule_id, current_user.id, db)
    if rule.is_default:
        raise HTTPException(status_code=409, detail="default rules cannot be deleted")
    db.delete(rule)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
