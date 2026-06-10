from pydantic import BaseModel


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    role: str | None = None

    class Config:
        from_attributes = True
