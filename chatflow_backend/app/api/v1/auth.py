from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth import LoginRequest, SignupResponse, UserCreate, UserRead
from app.services.auth_service import EmailAlreadyRegistered, authenticate_user, create_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/health")
def auth_health():
    return {"status": "ok"}


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        created_user = create_user(db, user)
    except EmailAlreadyRegistered as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        ) from exc

    created_id = cast(int, created_user.id)
    created_name = cast(str, created_user.name)
    created_email = cast(str, created_user.email)

    return SignupResponse(
        id=created_id,
        name=created_name,
        email=created_email,
    )


@router.post("/login", response_model=UserRead)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, str(credentials.email), credentials.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserRead(
        id=cast(int, user.id),
        name=cast(str, user.name),
        email=cast(str, user.email),
    )


