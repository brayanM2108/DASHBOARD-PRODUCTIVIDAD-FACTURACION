from fastapi import APIRouter, Depends, HTTPException, status

from ...services.manual_billing_service import ManualBillingService
from ..schemas.administrative_process import ProcessCreate, ProcessUpdate, ProcessOut, ProcessSummary
from ..deps import get_current_user, get_current_biller_name, get_manual_billing_service

router = APIRouter(
    prefix="/administrative-processes",
    tags=["administrative-processes"],
)


def _resolve_usuario_id(current_user, forced_user):
    if forced_user is not None:
        return current_user.id
    return None


@router.post("/", response_model=ProcessOut, status_code=status.HTTP_201_CREATED)
def create_process(
    payload: ProcessCreate,
    service: ManualBillingService = Depends(get_manual_billing_service),
    current_user=Depends(get_current_user),
):
    record = service.create_process(
        fecha=payload.fecha,
        proceso=payload.proceso,
        cantidad=payload.cantidad,
        observacion=payload.observacion,
        usuario_id=current_user.id,
    )
    return record


@router.get("/filter-options")
def get_filter_options(
    service: ManualBillingService = Depends(get_manual_billing_service),
    current_user=Depends(get_current_user),
    forced_user=Depends(get_current_biller_name),
):
    usuario_id = _resolve_usuario_id(current_user, forced_user)
    records = service.list_processes(usuario_id=usuario_id)
    df = service.to_dataframe(records) if records else None
    if df is None or df.empty:
        return {"people": [], "processes": []}
    return {
        "people": sorted(df["NOMBRE"].dropna().astype(str).unique().tolist()),
        "processes": sorted(df["PROCESO"].dropna().astype(str).unique().tolist()),
    }


@router.get("/summary/global", response_model=ProcessSummary)
def get_summary(
    fecha_desde=None,
    fecha_hasta=None,
    proceso=None,
    service: ManualBillingService = Depends(get_manual_billing_service),
    current_user=Depends(get_current_user),
    forced_user=Depends(get_current_biller_name),
):
    usuario_id = _resolve_usuario_id(current_user, forced_user)
    records = service.list_processes(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        proceso=proceso,
        usuario_id=usuario_id,
    )
    df = service.to_dataframe(records)
    if df.empty:
        return ProcessSummary(total_records=0, total_quantity=0, unique_people=0, unique_processes=0)
    from ...services.manual_billing_service import build_processes_kpis
    kpis = build_processes_kpis(df)
    return ProcessSummary(**kpis)


@router.get("/{process_id}", response_model=ProcessOut)
def get_process(
    process_id: int,
    service: ManualBillingService = Depends(get_manual_billing_service),
    current_user=Depends(get_current_user),
):
    record = service.get_process(process_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Process not found")
    return record


@router.get("/", response_model=list[ProcessOut])
def list_processes(
    fecha_desde=None,
    fecha_hasta=None,
    proceso=None,
    skip: int = 0,
    limit: int = 1000,
    service: ManualBillingService = Depends(get_manual_billing_service),
    current_user=Depends(get_current_user),
    forced_user=Depends(get_current_biller_name),
):
    usuario_id = _resolve_usuario_id(current_user, forced_user)
    return service.list_processes(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        proceso=proceso,
        usuario_id=usuario_id,
        skip=skip,
        limit=limit,
    )


@router.put("/{process_id}", response_model=ProcessOut)
def update_process(
    process_id: int,
    payload: ProcessUpdate,
    service: ManualBillingService = Depends(get_manual_billing_service),
    current_user=Depends(get_current_user),
):
    record = service.update_process(
        process_id,
        fecha=payload.fecha,
        proceso=payload.proceso,
        cantidad=payload.cantidad,
        observacion=payload.observacion,
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Process not found")
    return record


@router.delete("/{process_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_process(
    process_id: int,
    service: ManualBillingService = Depends(get_manual_billing_service),
    current_user=Depends(get_current_user),
):
    deleted = service.delete_process(process_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Process not found")
