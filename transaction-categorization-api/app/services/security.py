"""Hash passwords and create or verify short-lived login tokens."""

from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from uuid import uuid4

import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import settings


ALGORITHM = "HS256"
password_hasher = PasswordHash.recommended()


@dataclass(frozen=True)
class TokenClaims:
    user_id: int
    token_id: str
    expires_at: datetime


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    return password_hasher.verify(password, stored_hash)


def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.access_token_minutes)
    return jwt.encode(
        {
            "sub": str(user_id),
            "jti": uuid4().hex,
            "iat": now,
            "exp": expires_at,
        },
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def read_access_token(token: str) -> TokenClaims:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return TokenClaims(
            user_id=int(payload["sub"]),
            token_id=str(payload["jti"]),
            expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        )
    except (InvalidTokenError, KeyError, TypeError, ValueError) as error:
        raise ValueError("invalid or expired token") from error
