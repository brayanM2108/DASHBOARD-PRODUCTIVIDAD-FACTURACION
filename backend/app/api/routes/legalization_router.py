# app/api/routes/legalizations_router.py

from datetime import date

from fastapi import APIRouter, Query, Depends

from ..deps import (
    get_legalizations_service,
    get_current_biller_name,
    get_current_user,
)
from ..schemas.legalizations import LegalizationMetricsResponse

from ...services.legalizations_service import (
    LegalizationsService
)

router = APIRouter(
    prefix="/legalizations",
    tags=["Legalizations"],
)


@router.get("/metrics", response_model=LegalizationMetricsResponse)
def get_metrics(
        start_date: date,
        end_date: date,
        selected_users: list[str] | None = Query(default=None),
        service: LegalizationsService = Depends(
            get_legalizations_service
        ),
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