from dataclasses import dataclass


@dataclass
class TokenResponse:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@dataclass
class User:
    id: int | None = None
    username: str | None = None
    email: str | None = None
    document: str | None = None
    is_active: bool = True