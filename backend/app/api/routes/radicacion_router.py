from datetime import date

from fastapi import APIRouter, Query, Depends

from ..deps import get_radicacion_service, require_roles
from ..schemas.radicacion import RadicacionMetricsResponse
from ...services.radicacion_service import RadicacionService

router = APIRouter(
    prefix="/radicacion",
    tags=["Radicacion"],
)


@router.get("/metrics", response_model=RadicacionMetricsResponse)
def get_metrics(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    selected_users: list[str] | None = Query(default=None),
    service: RadicacionService = Depends(get_radicacion_service),
    current_user=Depends(require_roles("ADMIN", "SUPERVISOR")),
):
    return service.get_metrics(
        start_date=start_date,
        end_date=end_date,
        selected_users=selected_users,
    )
