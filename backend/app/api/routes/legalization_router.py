# app/api/routes/legalizations_router.py

from datetime import date

from fastapi import APIRouter, Query, Depends

from ..deps import (
    get_legalizations_service,
    require_roles
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

        current_user=Depends(
            require_roles("ADMIN", "SUPERVISOR")
        )
):
    return service.get_metrics(
        start_date=start_date,
        end_date=end_date,
        selected_users=selected_users,
    )