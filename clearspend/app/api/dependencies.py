"""Provide shared helpers that API routes need during a request."""

from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.revoked_token import RevokedToken
from app.models.user import User
from app.services.security import read_access_token


bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    """Give one database session to a request and close it afterward."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def authentication_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="valid authentication is required",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise authentication_error()

    try:
        claims = read_access_token(credentials.credentials)
    except ValueError as error:
        raise authentication_error() from error

    is_revoked = (
        db.query(RevokedToken.id)
        .filter(RevokedToken.token_id == claims.token_id)
        .first()
        is not None
    )
    if is_revoked:
        raise authentication_error()

    user = db.get(User, claims.user_id)
    if user is None or not user.is_active:
        raise authentication_error()
    return user
