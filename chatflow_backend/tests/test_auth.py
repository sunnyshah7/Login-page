import time
from types import SimpleNamespace
from unittest.mock import Mock

import jwt
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.api.v1 import auth
from app.core.config import settings
from app.core.security import create_access_token
from app.db.database import get_db
from app.schemas.auth import LoginRequest, UserCreate
from app.services.auth_service import EmailAlreadyRegistered, password_hash


def make_user() -> UserCreate:
    return UserCreate(name="Test User", email="test@example.com", password="secret")


def test_signup_duplicate_email_returns_409(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_duplicate(db: object, user: UserCreate) -> None:
        raise EmailAlreadyRegistered

    monkeypatch.setattr(auth, "create_user", raise_duplicate)

    with pytest.raises(HTTPException) as error:
        auth.signup(make_user(), db=object())

    assert error.value.status_code == 409


def test_signup_unexpected_error_is_not_converted_to_client_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_database_error(db: object, user: UserCreate) -> None:
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(auth, "create_user", raise_database_error)

    with pytest.raises(RuntimeError, match="database unavailable"):
        auth.signup(make_user(), db=object())


@pytest.mark.parametrize(
    "stored_user",
    [
        None,
        SimpleNamespace(hashed_password=password_hash.hash("different-password")),
    ],
    ids=["unknown-email", "incorrect-password"],
)
def test_login_uses_same_401_for_unknown_email_and_incorrect_password(
    stored_user: object | None,
) -> None:
    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = stored_user

    with pytest.raises(HTTPException) as error:
        auth.login(
            LoginRequest(email="test@example.com", password="wrong-password"),
            db=db,
        )

    assert error.value.status_code == 401
    assert error.value.detail == "Invalid email or password"


def test_login_returns_short_lived_jwt(monkeypatch: pytest.MonkeyPatch) -> None:
    secret = "test-only-secret-that-is-long-enough"
    monkeypatch.setattr(settings, "JWT_SECRET_KEY", secret)
    monkeypatch.setattr(settings, "JWT_ALGORITHM", "HS256")
    stored_user = SimpleNamespace(
        id=42,
        name="Test User",
        email="test@example.com",
        hashed_password=password_hash.hash("correct-password"),
    )
    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = stored_user

    response = auth.login(
        LoginRequest(email="test@example.com", password="correct-password"),
        db=db,
    )

    claims = jwt.decode(response.access_token, secret, algorithms=["HS256"])
    assert claims["sub"] == "42"
    assert 0 < claims["exp"] - time.time() <= 15 * 60
    assert response.token_type == "bearer"


@pytest.fixture
def auth_client(monkeypatch: pytest.MonkeyPatch) -> tuple[TestClient, Mock, str]:
    secret = "test-only-secret-that-is-long-enough"
    monkeypatch.setattr(settings, "JWT_SECRET_KEY", secret)
    monkeypatch.setattr(settings, "JWT_ALGORITHM", "HS256")
    db = Mock()
    app = FastAPI()
    app.include_router(auth.router)
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as client:
        yield client, db, secret
    app.dependency_overrides.clear()


def test_auth_me_returns_public_user_fields(auth_client: tuple[TestClient, Mock, str]) -> None:
    client, db, _ = auth_client
    db.query.return_value.filter.return_value.first.return_value = SimpleNamespace(
        id=42,
        name="Test User",
        email="test@example.com",
        hashed_password="must-not-be-returned",
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {create_access_token('42')}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 42,
        "name": "Test User",
        "email": "test@example.com",
    }


@pytest.mark.parametrize(
    "authorization",
    [
        None,
        "Bearer not-a-jwt",
        "Bearer " + jwt.encode(
            {"sub": "42", "exp": int(time.time()) - 1},
            "test-only-secret-that-is-long-enough",
            algorithm="HS256",
        ),
    ],
    ids=["missing", "invalid", "expired"],
)
def test_auth_me_rejects_missing_invalid_and_expired_tokens(
    auth_client: tuple[TestClient, Mock, str],
    authorization: str | None,
) -> None:
    client, _, _ = auth_client
    headers = {"Authorization": authorization} if authorization else {}

    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        ("/auth/signup", {"name": "Test User", "email": "invalid", "password": "secret"}),
        ("/auth/signup", {"name": "Test User", "email": "test@example.com"}),
        ("/auth/login", {"email": "invalid", "password": "secret"}),
        ("/auth/login", {"email": "test@example.com"}),
    ],
    ids=["signup-invalid-email", "signup-missing-password", "login-invalid-email", "login-missing-password"],
)
def test_auth_rejects_malformed_request_bodies_with_422(
    auth_client: tuple[TestClient, Mock, str],
    path: str,
    payload: dict[str, str],
) -> None:
    client, _, _ = auth_client

    response = client.post(path, json=payload)

    assert response.status_code == 422
