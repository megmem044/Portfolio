"""Password hashing, signed access tokens, and role checks."""

from __future__ import annotations

import base64
import binascii
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import os
import secrets
from uuid import uuid4

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db_models import UserRecord

TOKEN_LIFETIME_HOURS = 8
bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    if len(password) < 10:
        raise ValueError("Password must contain at least 10 characters.")
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return f"pbkdf2_sha256$310000${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, rounds, salt, expected = stored.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(rounds))
        return hmac.compare_digest(actual.hex(), expected)
    except (ValueError, TypeError):
        return False


def create_user(session: Session, email: str, password: str, role: str) -> UserRecord:
    normalized = email.strip().lower()
    selected_role = role.upper()
    if selected_role not in {"REVIEWER", "ADMIN"}:
        raise ValueError("Role must be REVIEWER or ADMIN.")
    if session.scalar(select(UserRecord).where(UserRecord.email == normalized)):
        raise ValueError("An account with that email already exists.")
    user = UserRecord(user_id=str(uuid4()), email=normalized, password_hash=hash_password(password), role=selected_role)
    session.add(user)
    session.flush()
    return user


def create_token(user: UserRecord) -> str:
    payload = {"sub": user.user_id, "role": user.role, "exp": int((datetime.now(timezone.utc) + timedelta(hours=TOKEN_LIFETIME_HOURS)).timestamp())}
    encoded = _encode(json.dumps(payload, separators=(",", ":")).encode())
    signature = _encode(hmac.new(_secret(), encoded.encode(), hashlib.sha256).digest())
    return f"{encoded}.{signature}"


def decode_token(token: str) -> dict:
    try:
        encoded, signature = token.split(".")
        expected = _encode(hmac.new(_secret(), encoded.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            raise ValueError
        payload = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
        if payload["exp"] < datetime.now(timezone.utc).timestamp():
            raise ValueError
        return payload
    except (ValueError, KeyError, json.JSONDecodeError, binascii.Error):
        raise HTTPException(status_code=401, detail="Sign in is required.") from None


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def _secret() -> bytes:
    return os.getenv("ANSWERTRUST_AUTH_SECRET", "local-development-secret-change-me").encode()


def require_roles(*roles: str):
    def dependency(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
        if credentials is None:
            raise HTTPException(status_code=401, detail="Sign in is required.")
        payload = decode_token(credentials.credentials)
        if payload["role"] not in roles:
            raise HTTPException(status_code=403, detail="You do not have permission to do this.")
        return payload
    return dependency
