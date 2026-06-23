from pydantic import BaseModel, Field
from typing import Optional

from .user import UserOut


class UserUpdate(BaseModel):
    """Schema for updating user fields."""
    email: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserListResponse(BaseModel):
    """Paginated user list response."""
    users: list[UserOut] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    size: int = 50
