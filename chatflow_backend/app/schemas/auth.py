from typing import Literal

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr  # this datatype will validate the correct email type
    password: str


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr


class SignupResponse(BaseModel):
    id: int
    name: str
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
