from typing import Literal

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Literal["student", "manager"]
    full_name: str


class UserResponse(BaseModel):
    id: str
    email: str
    role: Literal["student", "manager"]
    full_name: str
