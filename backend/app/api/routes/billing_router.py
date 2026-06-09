from datetime import date
from fastapi import APIRouter, Depends, Query

from ...services.billing_electronic_service import ElectronicBillingService
from ..deps import get_current_user, get_electronic_billing_service, require_roles
from ..schemas.billing import BillingMetricsResponse

router = APIRouter(
    prefix="/billing",
    tags=["billing"]
)


@router.get("/metrics", response_model=BillingMetricsResponse)
def get_metrics(
        start_date: date,
        end_date: date,
        selected_users: list[str] | None = Query(default=None),
        selected_agreement: str | None = Query(default=None),
        service: ElectronicBillingService = Depends(
            get_electronic_billing_service
        ),
        current_user=Depends(
            require_roles("ADMIN", "SUPERVISOR")
        ),
):
    result = service.get_metrics(
        start_date=start_date,
        end_date=end_date,
        selected_users=selected_users,
        selected_agreement=selected_agreement,
    )

    return BillingMetricsResponse(**result)
