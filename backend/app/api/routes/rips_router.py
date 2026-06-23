from datetime import date

from fastapi import APIRouter, Query, Depends

from ..deps import (
    get_rips_service,
    get_current_biller_name,
    get_current_user,
)
from ..schemas.rips import RipsMetricsResponse
from ...services.rips_service import RipsService

router = APIRouter(
    prefix="/rips",
    tags=["RIPS"],
)


@router.get("/metrics", response_model=RipsMetricsResponse)
def get_metrics(
    start_date: date,
    end_date: date,
    selected_users: list[str] | None = Query(default=None),
    service: RipsService = Depends(get_rips_service),
    current_user=Depends(get_current_user),
    forced_user=Depends(get_current_biller_name),
):
    if forced_user is not None:
        selected_users = [forced_user]

    return service.get_metrics(
        start_date=start_date,
        end_date=end_date,
        selected_users=selected_users,
    )
