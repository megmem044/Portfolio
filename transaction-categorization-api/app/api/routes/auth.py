"""Handle registration, login, logout, and current-user details."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import bearer_scheme, get_current_user, get_db
from app.core.config import settings
from app.models.user import User
from app.models.revoked_token import RevokedToken
from app.schemas.user import AccessToken, UserLogin, UserRead, UserRegister
from app.services.security import (
    create_access_token,
    hash_password,
    read_access_token,
    verify_password,
)


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    registration: UserRegister,
    db: Session = Depends(get_db),
):
    user = User(
        email=str(registration.email),
        password_hash=hash_password(registration.password),
        is_active=True,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail="email is already registered") from error

    db.refresh(user)
    return user


@router.post("/login", response_model=AccessToken)
def login_user(
    login: UserLogin,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == str(login.email)).one_or_none()
    if (
        user is None
        or not user.is_active
        or not verify_password(login.password, user.password_hash)
    ):
        raise HTTPException(status_code=401, detail="email or password is incorrect")

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
        "expires_in": settings.access_token_minutes * 60,
    }


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    claims = read_access_token(credentials.credentials)
    db.add(
        RevokedToken(
            token_id=claims.token_id,
            expires_at=claims.expires_at,
        )
    )
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
