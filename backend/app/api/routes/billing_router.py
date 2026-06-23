from datetime import date

from fastapi import APIRouter, Depends, Query

from ...services.billing_electronic_service import ElectronicBillingService
from ..deps import get_current_biller_name, get_current_user, get_electronic_billing_service
from ..schemas.billing import (
    BillingAnalyticsResponse,
    BillingDetailResponse,
    BillingSummaryResponse,
)

router = APIRouter(
    prefix="/billing",
    tags=["billing"],
)


def _resolve_selected_users(selected_users, forced_user):
    if forced_user is not None:
        return [forced_user]
    return selected_users


@router.get("/summary", response_model=BillingSummaryResponse)
def get_summary(
    start_date: date,
    end_date: date,
    selected_users: list[str] | None = Query(default=None),
    selected_agreement: str | None = Query(default=None),
    service: ElectronicBillingService = Depends(get_electronic_billing_service),
    current_user=Depends(get_current_user),
    forced_user=Depends(get_current_biller_name),
):
    selected_users = _resolve_selected_users(selected_users, forced_user)
    result = service.get_summary(
        start_date=start_date,
        end_date=end_date,
        selected_users=selected_users,
        selected_agreement=selected_agreement,
    )
    return BillingSummaryResponse(**result)


@router.get("/analytics", response_model=BillingAnalyticsResponse)
def get_analytics(
    start_date: date,
    end_date: date,
    selected_users: list[str] | None = Query(default=None),
    selected_agreement: str | None = Query(default=None),
    service: ElectronicBillingService = Depends(get_electronic_billing_service),
    current_user=Depends(get_current_user),
    forced_user=Depends(get_current_biller_name),
):
    selected_users = _resolve_selected_users(selected_users, forced_user)
    result = service.get_analytics(
        start_date=start_date,
        end_date=end_date,
        selected_users=selected_users,
        selected_agreement=selected_agreement,
    )
    return BillingAnalyticsResponse(**result)


@router.get("/detail", response_model=BillingDetailResponse)
def get_detail(
    start_date: date,
    end_date: date,
    selected_users: list[str] | None = Query(default=None),
    selected_agreement: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    filter_user: str | None = Query(default=None),
    filter_eps: str | None = Query(default=None),
    filter_convenio: str | None = Query(default=None),
    filter_estado: str | None = Query(default=None),
    service: ElectronicBillingService = Depends(get_electronic_billing_service),
    current_user=Depends(get_current_user),
    forced_user=Depends(get_current_biller_name),
):
    selected_users = _resolve_selected_users(selected_users, forced_user)
    result = service.get_detail(
        start_date=start_date,
        end_date=end_date,
        selected_users=selected_users,
        selected_agreement=selected_agreement,
        page=page,
        page_size=page_size,
        filter_user=filter_user,
        filter_eps=filter_eps,
        filter_convenio=filter_convenio,
        filter_estado=filter_estado,
    )
    return BillingDetailResponse(**result)
