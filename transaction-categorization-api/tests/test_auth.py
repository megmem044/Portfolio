"""Test registration, login, token use, and common authentication errors."""

from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings
from app.services.security import ALGORITHM


def register_user(client, email="person@example.com", password="StrongPass123"):
    return client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )


def login_user(client, email="person@example.com", password="StrongPass123"):
    return client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )


def test_register_user_returns_safe_account_details(client):
    response = register_user(client, email="Person@Example.com")

    assert response.status_code == 201
    assert response.json()["email"] == "person@example.com"
    assert response.json()["is_active"] is True
    assert "password" not in response.json()
    assert "password_hash" not in response.json()


def test_registration_validates_email_and_password(client):
    invalid_email = register_user(client, email="not-an-email")
    short_password = register_user(client, password="short")

    assert invalid_email.status_code == 422
    assert short_password.status_code == 422


def test_duplicate_email_is_rejected_case_insensitively(client):
    assert register_user(client).status_code == 201

    response = register_user(client, email="PERSON@example.com")

    assert response.status_code == 409
    assert response.json()["detail"] == "email is already registered"


def test_login_returns_bearer_token(client):
    register_user(client)

    response = login_user(client)

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["expires_in"] == 1800
    assert response.json()["access_token"]


def test_login_uses_generic_error_for_incorrect_credentials(client):
    register_user(client)

    wrong_password = login_user(client, password="WrongPass123")
    missing_email = login_user(client, email="missing@example.com")

    assert wrong_password.status_code == 401
    assert missing_email.status_code == 401
    assert wrong_password.json()["detail"] == "email or password is incorrect"
    assert missing_email.json()["detail"] == "email or password is incorrect"


def test_current_user_requires_valid_token(client):
    missing = client.get("/auth/me", headers={"Authorization": ""})
    invalid = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert missing.status_code == 401
    assert invalid.status_code == 401
    assert missing.headers["www-authenticate"] == "Bearer"


def test_current_user_is_returned_for_valid_token(client):
    registered = register_user(client).json()
    token = login_user(client).json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == registered


def test_logout_immediately_revokes_token(client):
    register_user(client)
    token = login_user(client).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    logout = client.post("/auth/logout", headers=headers)
    after_logout = client.get("/auth/me", headers=headers)

    assert logout.status_code == 204
    assert after_logout.status_code == 401


def test_expired_token_is_rejected(client):
    expired_token = jwt.encode(
        {
            "sub": "1",
            "jti": "expired-token-id",
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        },
        settings.secret_key,
        algorithm=ALGORITHM,
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401
