from ..repositories.user_repository import UserRepository
from ..core.exceptions.business import DataNotFoundException


class UsersService:
    """Service for user management operations."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def list_users(
        self,
        page: int = 1,
        size: int = 50,
        search: str | None = None,
        role_filter: str | None = None,
    ) -> dict:
        """List users with pagination, search, and role filter."""
        users, total = self.user_repo.get_all_paginated(
            page=page,
            size=size,
            search=search,
            role_filter=role_filter,
        )

        return {
            "users": users,
            "total": total,
            "page": page,
            "size": size,
        }

    def get_user(self, user_id: int) -> dict:
        """Get user by ID."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise DataNotFoundException(f"User with id {user_id} not found")
        return user

    def update_user(self, user_id: int, data: dict) -> dict:
        """Update user fields."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise DataNotFoundException(f"User with id {user_id} not found")

        update_data = {k: v for k, v in data.items() if v is not None}
        if not update_data:
            return user

        return self.user_repo.update(user, **update_data)

    def toggle_active(self, user_id: int) -> dict:
        """Toggle user active status."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise DataNotFoundException(f"User with id {user_id} not found")

        new_status = not user.is_active
        return self.user_repo.update(user, is_active=new_status)
