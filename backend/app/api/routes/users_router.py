from fastapi import APIRouter, Depends, Query

from ...services.users_service import UsersService
from ..deps import get_current_user, require_roles
from ..deps.service_deps import get_users_service
from ..schemas.user import UserOut
from ..schemas.users import UserUpdate, UserListResponse

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("", response_model=UserListResponse)
def list_users(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=100),
    search: str | None = Query(default=None),
    role_filter: str | None = Query(default=None),
    service: UsersService = Depends(get_users_service),
    current_user=Depends(require_roles("ADMIN")),
):
    result = service.list_users(page, size, search, role_filter)
    return UserListResponse(**result)


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    service: UsersService = Depends(get_users_service),
    current_user=Depends(require_roles("ADMIN")),
):
    user = service.get_user(user_id)
    return UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        role=user.role,
    )


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    data: UserUpdate,
    service: UsersService = Depends(get_users_service),
    current_user=Depends(require_roles("ADMIN")),
):
    update_data = data.model_dump(exclude_unset=True)
    user = service.update_user(user_id, update_data)
    return UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        role=user.role,
    )


@router.patch("/{user_id}/toggle", response_model=UserOut)
def toggle_active(
    user_id: int,
    service: UsersService = Depends(get_users_service),
    current_user=Depends(require_roles("ADMIN")),
):
    user = service.toggle_active(user_id)
    return UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        role=user.role,
    )
