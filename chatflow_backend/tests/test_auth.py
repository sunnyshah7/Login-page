import pytest
from fastapi import HTTPException
from types import SimpleNamespace
from unittest.mock import Mock

from app.api.v1 import auth
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
