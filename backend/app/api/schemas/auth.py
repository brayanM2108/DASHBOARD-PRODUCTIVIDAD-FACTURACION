from typing import Any

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict[str, Any] | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    document: str
    username: str
    password: str
    role: str | None = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str
