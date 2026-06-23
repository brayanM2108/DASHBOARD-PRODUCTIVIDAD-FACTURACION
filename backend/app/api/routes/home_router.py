from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query

from ...services.home_service import HomeService
from ..deps import get_current_user, require_roles, get_current_biller_name
from ..deps.service_deps import get_home_service
from ..schemas.home import HomeAdminResponse, HomeUserResponse

router = APIRouter(prefix="/home", tags=["home"])


@router.get("/admin/summary", response_model=HomeAdminResponse)
def get_admin_summary(
    start_date: date = Query(default=None),
    end_date: date = Query(default=None),
    filter_user: str | None = Query(default=None),
    service: HomeService = Depends(get_home_service),
    current_user=Depends(require_roles("ADMIN", "SUPERVISOR")),
):
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=29)

    return service.get_admin_summary(start_date, end_date, filter_user)


@router.get("/user/summary", response_model=HomeUserResponse)
def get_user_summary(
    start_date: date = Query(default=None),
    end_date: date = Query(default=None),
    service: HomeService = Depends(get_home_service),
    current_user=Depends(get_current_user),
    biller_name=Depends(get_current_biller_name),
):
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=29)

    return service.get_user_summary(biller_name, start_date, end_date)
