"""
Export Router — Download Excel reports
=======================================
Endpoints that generate and return Excel files for download.
"""

import logging
import pandas as pd
from datetime import date, timedelta
from io import BytesIO

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from ...etl.excel_exporter import (
    export_billing_report,
    export_general_report,
    export_legalizations_report,
    export_processes_report,
    export_radicacion_report,
    export_rips_report,
)
from ...etl.filters.legalizations_filter import filter_legalizations
from ...etl.filters.rips_filter import filter_rips
from ...etl.radicacion_processor import prepare_radicacion_df
from ...repositories.administrative_process_repository import AdministrativeProcessRepository
from ...repositories.user_repository import UserRepository
from ...services.billing_electronic_service import ElectronicBillingService
from ...services.legalizations_service import LegalizationsService
from ...services.manual_billing_service import ManualBillingService
from ...services.radicacion_service import RadicacionService
from ...services.report_service import (
    build_billing_report,
    build_general_report,
    build_legalizations_report,
    build_processes_report,
    build_radicacion_report,
    build_rips_report,
)
from ...services.rips_service import RipsService
from ..deps import (
    get_current_biller_name,
    get_current_user,
    get_electronic_billing_service,
    get_legalizations_service,
    get_manual_billing_service,
    get_radicacion_service,
    get_rips_service,
)
from ..deps.repository_deps import (
    get_administrative_process_repository,
    get_user_repository,
)

router = APIRouter(
    prefix="/export",
    tags=["export"],
)


def _resolve_selected_users(selected_users, forced_user):
    if forced_user is not None:
        return [forced_user]
    return selected_users


def _make_period_label(start_date: date, end_date: date) -> str:
    return f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"


def _bytes_response(file_bytes: bytes, filename: str) -> StreamingResponse:
    return StreamingResponse(
        BytesIO(file_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ---------------------------------------------------------------------------
# Billing export
# ---------------------------------------------------------------------------

@router.get("/billing")
def export_billing(
    start_date: date = Query(...),
    end_date: date = Query(...),
    selected_users: list[str] | None = Query(default=None),
    service: ElectronicBillingService = Depends(get_electronic_billing_service),
    current_user=Depends(get_current_user),
    forced_user=Depends(get_current_biller_name),
):
    selected_users = _resolve_selected_users(selected_users, forced_user)
    df = service._load_and_filter(start_date, end_date, selected_users)

    # Previous period for comparison
    days = (end_date - start_date).days + 1
    prev_start = start_date - timedelta(days=days)
    prev_end = start_date - timedelta(days=1)
    logger = logging.getLogger(__name__)
    df_previous = None
    try:
        df_previous = service._load_and_filter(prev_start, prev_end, selected_users)
    except Exception as e:
        logger.warning("Billing previous period unavailable: %s", e)

    report = build_billing_report(df_current=df, df_previous=df_previous)
    file_bytes = export_billing_report(report, period_label=_make_period_label(start_date, end_date))
    return _bytes_response(file_bytes, f"informe_facturacion_{start_date}_{end_date}.xlsx")


# ---------------------------------------------------------------------------
# Legalizations export
# ---------------------------------------------------------------------------

@router.get("/legalizations")
def export_legalizations(
    start_date: date = Query(...),
    end_date: date = Query(...),
    selected_users: list[str] | None = Query(default=None),
    service: LegalizationsService = Depends(get_legalizations_service),
    current_user=Depends(get_current_user),
    forced_user=Depends(get_current_biller_name),
):
    selected_users = _resolve_selected_users(selected_users, forced_user)
    df = service.get_processed_data()

    df_filtered = filter_legalizations(df, start_date, end_date, selected_users)

    days = (end_date - start_date).days + 1
    prev_start = start_date - timedelta(days=days)
    prev_end = start_date - timedelta(days=1)
    df_previous = filter_legalizations(df, prev_start, prev_end, selected_users)

    report = build_legalizations_report(
        legalizations_current=df_filtered,
        legalizations_previous=df_previous,
    )
    file_bytes = export_legalizations_report(report, period_label=_make_period_label(start_date, end_date))
    return _bytes_response(file_bytes, f"informe_legalizaciones_{start_date}_{end_date}.xlsx")


# ---------------------------------------------------------------------------
# RIPS export
# ---------------------------------------------------------------------------

@router.get("/rips")
def export_rips(
    start_date: date = Query(...),
    end_date: date = Query(...),
    selected_users: list[str] | None = Query(default=None),
    service: RipsService = Depends(get_rips_service),
    current_user=Depends(get_current_user),
    forced_user=Depends(get_current_biller_name),
):
    selected_users = _resolve_selected_users(selected_users, forced_user)
    df = service.get_processed_data()

    df_filtered = filter_rips(df, start_date, end_date, selected_users)

    days = (end_date - start_date).days + 1
    prev_start = start_date - timedelta(days=days)
    prev_end = start_date - timedelta(days=1)
    df_previous = filter_rips(df, prev_start, prev_end, selected_users)

    report = build_rips_report(df_current=df_filtered, df_previous=df_previous)
    file_bytes = export_rips_report(report, period_label=_make_period_label(start_date, end_date))
    return _bytes_response(file_bytes, f"informe_rips_{start_date}_{end_date}.xlsx")


# ---------------------------------------------------------------------------
# Radicación export
# ---------------------------------------------------------------------------

@router.get("/radicacion")
def export_radicacion(
    start_date: date = Query(...),
    end_date: date = Query(...),
    selected_users: list[str] | None = Query(default=None),
    service: RadicacionService = Depends(get_radicacion_service),
    current_user=Depends(get_current_user),
    forced_user=Depends(get_current_biller_name),
):
    selected_users = _resolve_selected_users(selected_users, forced_user)
    metrics = service.get_metrics(start_date, end_date, selected_users)

    df = service.repository.load()
    df_prepared = prepare_radicacion_df(df)

    fecha_col = "FECHA FACTURA"
    if fecha_col in df_prepared.columns:
        df_prepared = df_prepared[df_prepared[fecha_col].dt.date >= start_date]
        df_prepared = df_prepared[df_prepared[fecha_col].dt.date <= end_date]

    user_col = "USUARIO"
    if selected_users and user_col in df_prepared.columns:
        selected_set = {str(u).strip().upper() for u in selected_users}
        df_prepared = df_prepared[
            df_prepared[user_col].astype(str).str.strip().str.upper().isin(selected_set)
        ]

    days = (end_date - start_date).days + 1
    prev_start = start_date - timedelta(days=days)
    prev_end = start_date - timedelta(days=1)
    df_previous = df_prepared.copy()
    if fecha_col in df_previous.columns:
        df_previous = df_previous[df_previous[fecha_col].dt.date >= prev_start]
        df_previous = df_previous[df_previous[fecha_col].dt.date <= prev_end]

    report = build_radicacion_report(df_current=df_prepared, df_previous=df_previous)
    file_bytes = export_radicacion_report(report, period_label=_make_period_label(start_date, end_date))
    return _bytes_response(file_bytes, f"informe_radicacion_{start_date}_{end_date}.xlsx")


# ---------------------------------------------------------------------------
# Processes export
# ---------------------------------------------------------------------------

@router.get("/processes")
def export_processes(
    start_date: date = Query(...),
    end_date: date = Query(...),
    selected_users: list[str] | None = Query(default=None),
    service: ManualBillingService = Depends(get_manual_billing_service),
    current_user=Depends(get_current_user),
    forced_user=Depends(get_current_biller_name),
    processes_repo: AdministrativeProcessRepository = Depends(get_administrative_process_repository),
    user_repo: UserRepository = Depends(get_user_repository),
):
    # Get user_id for filtering
    user_id = None
    if forced_user and forced_user not in ("__no_document__", "__no_match__"):
        user = user_repo.get_by_username(forced_user)
        if user:
            user_id = user.id

    processes = processes_repo.list(
        fecha_desde=start_date,
        fecha_hasta=end_date,
        usuario_id=user_id,
    )

    if processes:
        proc_data = [
            {"FECHA": p.fecha, "NOMBRE": p.nombre, "PROCESO": p.proceso, "CANTIDAD": p.cantidad}
            for p in processes
        ]
        df = pd.DataFrame(proc_data)
    else:
        df = pd.DataFrame(columns=["FECHA", "NOMBRE", "PROCESO", "CANTIDAD"])

    days = (end_date - start_date).days + 1
    prev_start = start_date - timedelta(days=days)
    prev_end = start_date - timedelta(days=1)
    prev_processes = processes_repo.list(
        fecha_desde=prev_start,
        fecha_hasta=prev_end,
        usuario_id=user_id,
    )
    df_previous = None
    if prev_processes:
        prev_data = [
            {"FECHA": p.fecha, "NOMBRE": p.nombre, "PROCESO": p.proceso, "CANTIDAD": p.cantidad}
            for p in prev_processes
        ]
        df_previous = pd.DataFrame(prev_data)

    report = build_processes_report(df_current=df, df_previous=df_previous)
    file_bytes = export_processes_report(report, period_label=_make_period_label(start_date, end_date))
    return _bytes_response(file_bytes, f"informe_procesos_{start_date}_{end_date}.xlsx")


# ---------------------------------------------------------------------------
# General export (all modules combined)
# ---------------------------------------------------------------------------

@router.get("/general")
def export_general(
    start_date: date = Query(...),
    end_date: date = Query(...),
    selected_users: list[str] | None = Query(default=None),
    billing_service: ElectronicBillingService = Depends(get_electronic_billing_service),
    legalizations_service: LegalizationsService = Depends(get_legalizations_service),
    rips_service: RipsService = Depends(get_rips_service),
    radicacion_service: RadicacionService = Depends(get_radicacion_service),
    processes_service: ManualBillingService = Depends(get_manual_billing_service),
    processes_repo: AdministrativeProcessRepository = Depends(get_administrative_process_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    current_user=Depends(get_current_user),
    forced_user=Depends(get_current_biller_name),
):
    selected_users = _resolve_selected_users(selected_users, forced_user)
    period_label = _make_period_label(start_date, end_date)

    logger = logging.getLogger(__name__)
    days = (end_date - start_date).days + 1
    prev_start = start_date - timedelta(days=days)
    prev_end = start_date - timedelta(days=1)

    # Billing
    billing_report = None
    try:
        df_bill = billing_service._load_and_filter(start_date, end_date, selected_users)
        df_bill_prev = None
        try:
            df_bill_prev = billing_service._load_and_filter(prev_start, prev_end, selected_users)
        except Exception as e:
            logger.warning("General export: billing previous period unavailable: %s", e)
        billing_report = build_billing_report(df_current=df_bill, df_previous=df_bill_prev)
    except Exception as e:
        logger.warning("General export: billing section failed: %s", e)

    # Legalizations
    legalizations_report = None
    try:
        df_leg = legalizations_service.get_processed_data()
        df_leg_filtered = filter_legalizations(df_leg, start_date, end_date, selected_users)
        df_leg_prev = filter_legalizations(df_leg, prev_start, prev_end, selected_users)
        legalizations_report = build_legalizations_report(
            legalizations_current=df_leg_filtered,
            legalizations_previous=df_leg_prev,
        )
    except Exception as e:
        logger.warning("General export: legalizations section failed: %s", e)

    # RIPS
    rips_report = None
    try:
        df_rips = rips_service.get_processed_data()
        df_rips_filtered = filter_rips(df_rips, start_date, end_date, selected_users)
        df_rips_prev = filter_rips(df_rips, prev_start, prev_end, selected_users)
        rips_report = build_rips_report(df_current=df_rips_filtered, df_previous=df_rips_prev)
    except Exception as e:
        logger.warning("General export: RIPS section failed: %s", e)

    # Radicación
    radicacion_report = None
    try:
        df_rad = radicacion_service.repository.load()
        df_rad_prepared = prepare_radicacion_df(df_rad)
        fecha_col = "FECHA FACTURA"
        if fecha_col in df_rad_prepared.columns:
            df_rad_prepared = df_rad_prepared[df_rad_prepared[fecha_col].dt.date >= start_date]
            df_rad_prepared = df_rad_prepared[df_rad_prepared[fecha_col].dt.date <= end_date]
        user_col = "USUARIO"
        if selected_users and user_col in df_rad_prepared.columns:
            selected_set = {str(u).strip().upper() for u in selected_users}
            df_rad_prepared = df_rad_prepared[
                df_rad_prepared[user_col].astype(str).str.strip().str.upper().isin(selected_set)
            ]
        df_rad_prev = df_rad_prepared.copy()
        if fecha_col in df_rad_prev.columns:
            df_rad_prev = df_rad_prev[df_rad_prev[fecha_col].dt.date >= prev_start]
            df_rad_prev = df_rad_prev[df_rad_prev[fecha_col].dt.date <= prev_end]
        radicacion_report = build_radicacion_report(df_current=df_rad_prepared, df_previous=df_rad_prev)
    except Exception as e:
        logger.warning("General export: radicacion section failed: %s", e)

    # Processes
    processes_report = None
    try:
        user_id = None
        if forced_user and forced_user not in ("__no_document__", "__no_match__"):
            user = user_repo.get_by_username(forced_user)
            if user:
                user_id = user.id

        processes = processes_repo.list(
            fecha_desde=start_date, fecha_hasta=end_date, usuario_id=user_id,
        )
        if processes:
            proc_data = [
                {"FECHA": p.fecha, "NOMBRE": p.nombre, "PROCESO": p.proceso, "CANTIDAD": p.cantidad}
                for p in processes
            ]
            df_proc = pd.DataFrame(proc_data)
        else:
            df_proc = pd.DataFrame(columns=["FECHA", "NOMBRE", "PROCESO", "CANTIDAD"])

        prev_processes = processes_repo.list(
            fecha_desde=prev_start, fecha_hasta=prev_end, usuario_id=user_id,
        )
        df_proc_prev = None
        if prev_processes:
            prev_data = [
                {"FECHA": p.fecha, "NOMBRE": p.nombre, "PROCESO": p.proceso, "CANTIDAD": p.cantidad}
                for p in prev_processes
            ]
            df_proc_prev = pd.DataFrame(prev_data)

        processes_report = build_processes_report(df_current=df_proc, df_previous=df_proc_prev)
    except Exception as e:
        logger.warning("General export: processes section failed: %s", e)

    general_report = build_general_report(
        billing_report=billing_report,
        legalizations_report=legalizations_report,
        rips_report=rips_report,
        radicacion_report=radicacion_report,
        processes_report=processes_report,
    )

    file_bytes = export_general_report(general_report, period_label=period_label)
    return _bytes_response(file_bytes, f"informe_general_{start_date}_{end_date}.xlsx")
