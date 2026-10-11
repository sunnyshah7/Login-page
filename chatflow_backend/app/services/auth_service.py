from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import UserCreate
from pwdlib import PasswordHash


# def create_user(db: Session, user: UserCreate) -> User:
#     db_user = User(name=user.name, email=user.email, password=user.password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user




password_hash = PasswordHash.recommended()


class EmailAlreadyRegistered(Exception):
    pass


def create_user(db: Session, user: UserCreate) -> User:
    email = str(user.email).lower()

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user is not None:
        raise EmailAlreadyRegistered

    db_user = User(
        name=user.name,
        email=email,
        hashed_password=password_hash.hash(user.password),
    )

    db.add(db_user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        duplicate_email = db.query(User).filter(User.email == email).first()
        if duplicate_email is not None:
            raise EmailAlreadyRegistered from exc
        raise

    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    normalized_email = email.lower()
    user = db.query(User).filter(User.email == normalized_email).first()

    if user is None or not password_hash.verify(password, user.hashed_password):
        return None

    return user