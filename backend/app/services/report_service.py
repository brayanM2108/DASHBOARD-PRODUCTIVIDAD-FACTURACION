"""
Business logic - Report Service
================================
Builds structured report data for each module.
Consumed by excel_exporter.py to generate downloadable Excel files.
"""

import pandas as pd
import streamlit as st

from ..etl.transformers.legalizations_transformer import (
    AGREEMENT_TYPE,
    PPL_TYPE,
)
from ..etl.filters.legalizations_filter import filter_legalizations
from .productivity_service import ProductivityService
from .manual_billing_service import build_chart_datasets, build_processes_kpis, get_summary_by_person, get_summary_by_process


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _calculate_variation(current: float, previous: float) -> float | None:
    """
    Percentage variation between two periods.
    Returns None when the previous value is zero or unavailable.
    """
    if previous is None or previous == 0:
        return None
    return ((current - previous) / previous) * 100


def _build_variation_block(current_total: float, previous_total: float) -> dict:
    """Return a standardized variation block for the executive summary."""
    variation = _calculate_variation(current_total, previous_total)
    return {
        "current_total": current_total,
        "previous_total": previous_total,
        "variation_pct": variation,
    }


def _top5_by_user(by_user_df: pd.DataFrame | None) -> pd.DataFrame | None:
    """Return the top 5 users by COUNT from a by_user dataframe."""
    if by_user_df is None or by_user_df.empty:
        return None
    if "COUNT" not in by_user_df.columns:
        return None
    return (
        by_user_df
        .sort_values("COUNT", ascending=False)
        .head(5)
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# Billing report
# ---------------------------------------------------------------------------

def build_billing_report(
        df_current: pd.DataFrame,
        df_previous: pd.DataFrame | None = None,
        by_user_df: pd.DataFrame | None = None,
) -> dict:
    """
    Build billing report data.

    Args:
        df_current: Filtered billing dataframe for the current period.
        df_previous: Filtered billing dataframe for the previous period (optional).
        by_user_df: Optional pre-aggregated productivity by user dataframe.

    Returns:
        dict with keys: executive_summary, by_user, by_date
    """
    metrics_current = ProductivityService.calculate_electronic_billing_productivity(df_current)
    metrics_previous = ProductivityService.calculate_electronic_billing_productivity(df_previous) if df_previous is not None else None

    by_user_current = by_user_df if by_user_df is not None else metrics_current["by_user"]

    previous_total = metrics_previous["total"] if metrics_previous else 0
    previous_daily_avg = metrics_previous["daily_average"] if metrics_previous else 0
    user_col = by_user_current.columns[0] if by_user_current is not None and not by_user_current.empty else "USUARIO"
    executive_summary = {
        "total": metrics_current["total"],
        "daily_average": metrics_current["daily_average"],
        "top5_by_user": _top5_by_user(by_user_current),
        "variation": _build_variation_block(metrics_current["total"], previous_total),
        "variation_daily_avg": _build_variation_block(
            metrics_current["daily_average"], previous_daily_avg
        ),
    }

    return {
        "executive_summary": executive_summary,
        "by_user": by_user_current,
        "by_date": metrics_current["by_date"],
        "by_date_records": (
            metrics_current["by_date_dual"][["DATE", "REGISTROS"]]
            if metrics_current.get("by_date_dual") is not None
            else None
        ),
        "by_user_records": (
            metrics_current["by_user_dual"][[user_col, "REGISTROS"]]
            if metrics_current.get("by_user_dual") is not None
            else None
        ),
    }


@st.cache_data(show_spinner=False, ttl=300)
def build_billing_report_cached(
        df_current: pd.DataFrame,
        df_previous: pd.DataFrame | None = None,
        by_user_df: pd.DataFrame | None = None,
) -> dict:
    """Cached wrapper for billing report generation."""
    return build_billing_report(df_current=df_current, df_previous=df_previous, by_user_df=by_user_df)


# ---------------------------------------------------------------------------
# Legalizations report (unified dataframe split by type)
# ---------------------------------------------------------------------------

def build_legalizations_report(
        legalizations_current: pd.DataFrame,
        legalizations_previous: pd.DataFrame | None = None,
) -> dict:
    """
    Build legalizations report data from the unified legalizations dataframe.

    Args:
        legalizations_current: Filtered legalizations dataframe for the current period.
        legalizations_previous: Legalizations dataframe for the previous period (optional).

    Returns:
        dict with keys: executive_summary, ppl, agreements
        - ppl / agreements each contain: metrics, by_user, by_date, top5_by_user
    """
    ppl_current = filter_legalizations(
        legalizations_current,
        start_date=None,
        end_date=None,
        legalization_type=PPL_TYPE,
    )
    agreements_current = filter_legalizations(
        legalizations_current,
        start_date=None,
        end_date=None,
        legalization_type=AGREEMENT_TYPE,
    )

    ppl_metrics = ProductivityService.calculate_legalizations_productivity(ppl_current, category="PPL")
    agreements_metrics = ProductivityService.calculate_legalizations_productivity(agreements_current, category="Convenios")

    ppl_previous = (
        filter_legalizations(
            legalizations_previous,
            start_date=None,
            end_date=None,
            legalization_type=PPL_TYPE,
        )
        if legalizations_previous is not None
        else None
    )
    agreements_previous = (
        filter_legalizations(
            legalizations_previous,
            start_date=None,
            end_date=None,
            legalization_type=AGREEMENT_TYPE,
        )
        if legalizations_previous is not None
        else None
    )

    ppl_previous_metrics = (
        ProductivityService.calculate_legalizations_productivity(ppl_previous, category="PPL")
        if ppl_previous is not None
        else None
    )
    agreements_previous_metrics = (
        ProductivityService.calculate_legalizations_productivity(agreements_previous, category="Convenios")
        if agreements_previous is not None
        else None
    )

    total_current = ppl_metrics["total"] + agreements_metrics["total"]
    total_previous = (
            (ppl_previous_metrics["total"] if ppl_previous_metrics else 0)
            + (agreements_previous_metrics["total"] if agreements_previous_metrics else 0)
    )

    # Weighted daily average across both categories
    ppl_avg = ppl_metrics["daily_average"] or 0
    agreements_avg = agreements_metrics["daily_average"] or 0
    global_daily_avg = (ppl_avg + agreements_avg) / 2 if (ppl_avg + agreements_avg) > 0 else 0

    ppl_prev_avg = ppl_previous_metrics["daily_average"] if ppl_previous_metrics else 0
    agreements_prev_avg = agreements_previous_metrics["daily_average"] if agreements_previous_metrics else 0
    previous_daily_avg = (ppl_prev_avg + agreements_prev_avg) / 2

    executive_summary = {
        "total": total_current,
        "daily_average": global_daily_avg,
        "ppl_total": ppl_metrics["total"],
        "agreements_total": agreements_metrics["total"],
        "variation": _build_variation_block(total_current, total_previous),
        "variation_daily_avg": _build_variation_block(global_daily_avg, previous_daily_avg),
    }

    # Convert lists to DataFrames (calculate_record_productivity returns lists)
    ppl_by_user = ppl_metrics["by_user"]
    if isinstance(ppl_by_user, list):
        ppl_by_user = pd.DataFrame(ppl_by_user) if ppl_by_user else None
    ppl_by_date = ppl_metrics["by_date"]
    if isinstance(ppl_by_date, list):
        ppl_by_date = pd.DataFrame(ppl_by_date) if ppl_by_date else None

    agr_by_user = agreements_metrics["by_user"]
    if isinstance(agr_by_user, list):
        agr_by_user = pd.DataFrame(agr_by_user) if agr_by_user else None
    agr_by_date = agreements_metrics["by_date"]
    if isinstance(agr_by_date, list):
        agr_by_date = pd.DataFrame(agr_by_date) if agr_by_date else None

    return {
        "executive_summary": executive_summary,
        "ppl": {
            "metrics": ppl_metrics,
            "by_user": ppl_by_user,
            "by_date": ppl_by_date,
            "top5_by_user": _top5_by_user(ppl_by_user),
        },
        "agreements": {
            "metrics": agreements_metrics,
            "by_user": agr_by_user,
            "by_date": agr_by_date,
            "top5_by_user": _top5_by_user(agr_by_user),
        },
    }


@st.cache_data(show_spinner=False, ttl=300)
def build_legalizations_report_cached(
        legalizations_current: pd.DataFrame,
        legalizations_previous: pd.DataFrame | None = None,
) -> dict:
    """Cached wrapper for legalizations report generation."""
    return build_legalizations_report(
        legalizations_current=legalizations_current,
        legalizations_previous=legalizations_previous,
    )


# ---------------------------------------------------------------------------
# Administrative processes report
# ---------------------------------------------------------------------------

def build_processes_report(
        df_current: pd.DataFrame,
        df_previous: pd.DataFrame | None = None,
        selected_person: str | None = None,
        selected_process: str | None = None,
) -> dict:
    """
    Build administrative processes report data.

    Args:
        df_current: Filtered processes dataframe for the current period.
        df_previous: Filtered processes dataframe for the previous period (optional).
        selected_person: Active person filter (for chart datasets).
        selected_process: Active process filter (for chart datasets).

    Returns:
        dict with keys: executive_summary, by_person, by_process, chart_datasets
    """
    kpis_current = build_processes_kpis(df_current)
    kpis_previous = build_processes_kpis(df_previous) if df_previous is not None else None

    previous_records = kpis_previous["total_records"] if kpis_previous else 0
    previous_quantity = kpis_previous["total_quantity"] if kpis_previous else 0

    executive_summary = {
        "total_records": kpis_current["total_records"],
        "total_quantity": kpis_current["total_quantity"],
        "unique_people": kpis_current["unique_people"],
        "unique_processes": kpis_current["unique_processes"],
        "variation_records": _build_variation_block(
            kpis_current["total_records"], previous_records
        ),
        "variation_quantity": _build_variation_block(
            kpis_current["total_quantity"], previous_quantity
        ),
    }

    chart_datasets = build_chart_datasets(
        df_current,
        selected_person=selected_person,
        selected_process=selected_process,
    )

    return {
        "executive_summary": executive_summary,
        "by_person": get_summary_by_person(df_current),
        "by_process": get_summary_by_process(df_current),
        "chart_datasets": chart_datasets,
    }


@st.cache_data(show_spinner=False, ttl=300)
def build_processes_report_cached(
        df_current: pd.DataFrame,
        df_previous: pd.DataFrame | None = None,
        selected_person: str | None = None,
        selected_process: str | None = None,
) -> dict:
    """Cached wrapper for administrative processes report generation."""
    return build_processes_report(
        df_current=df_current,
        df_previous=df_previous,
        selected_person=selected_person,
        selected_process=selected_process,
    )


# ---------------------------------------------------------------------------
# RIPS report
# ---------------------------------------------------------------------------

def build_rips_report(
        df_current: pd.DataFrame,
        df_previous: pd.DataFrame | None = None,
) -> dict:
    """
    Build RIPS report data.

    Args:
        df_current: Filtered RIPS dataframe for the current period.
        df_previous: Filtered RIPS dataframe for the previous period (optional).

    Returns:
        dict with keys: executive_summary, by_user, by_date
    """
    metrics_current = ProductivityService.calculate_record_productivity(
        df_current,
        user_column_variants=["NOMBRE_USUARIO"],
        date_column_variants=["FECHA_COMPLETADO_RIPS"],
        category="RIPS",
    )
    metrics_previous = ProductivityService.calculate_record_productivity(
        df_previous,
        user_column_variants=["NOMBRE_USUARIO"],
        date_column_variants=["FECHA_COMPLETADO_RIPS"],
        category="RIPS",
    ) if df_previous is not None else None

    previous_total = metrics_previous["total"] if metrics_previous else 0
    previous_daily_avg = metrics_previous["daily_average"] if metrics_previous else 0

    by_user_df = metrics_current.get("by_user")
    if by_user_df and isinstance(by_user_df, list):
        by_user_df = pd.DataFrame(by_user_df) if by_user_df else None

    executive_summary = {
        "total": metrics_current["total"],
        "daily_average": metrics_current["daily_average"],
        "top5_by_user": _top5_by_user(by_user_df),
        "variation": _build_variation_block(metrics_current["total"], previous_total),
        "variation_daily_avg": _build_variation_block(
            metrics_current["daily_average"], previous_daily_avg
        ),
    }

    by_date_df = metrics_current.get("by_date")
    if by_date_df and isinstance(by_date_df, list):
        by_date_df = pd.DataFrame(by_date_df) if by_date_df else None

    return {
        "executive_summary": executive_summary,
        "by_user": by_user_df,
        "by_date": by_date_df,
    }


@st.cache_data(show_spinner=False, ttl=300)
def build_rips_report_cached(
        df_current: pd.DataFrame,
        df_previous: pd.DataFrame | None = None,
) -> dict:
    """Cached wrapper for RIPS report generation."""
    return build_rips_report(df_current=df_current, df_previous=df_previous)


# ---------------------------------------------------------------------------
# Radicación report
# ---------------------------------------------------------------------------

def build_radicacion_report(
        df_current: pd.DataFrame,
        df_previous: pd.DataFrame | None = None,
) -> dict:
    """
    Build Radicación report data.

    Args:
        df_current: Filtered radicacion dataframe (from prepare_radicacion_df).
        df_previous: Filtered radicacion dataframe for previous period (optional).

    Returns:
        dict with keys: executive_summary, vencidas_df, by_user
    """
    total = len(df_current) if df_current is not None else 0
    vencidas = int(df_current["VENCIDA"].sum()) if df_current is not None and "VENCIDA" in df_current.columns else 0
    radicadas = total - vencidas
    pct_radicado = round((radicadas / total * 100), 1) if total > 0 else 0.0
    pct_vencidas = round((vencidas / total * 100), 1) if total > 0 else 0.0

    prev_total = len(df_previous) if df_previous is not None else 0
    prev_vencidas = int(df_previous["VENCIDA"].sum()) if df_previous is not None and "VENCIDA" in df_previous.columns else 0

    # Vencidas dataframe
    vencidas_df = None
    if df_current is not None and "VENCIDA" in df_current.columns:
        vencidas_only = df_current[df_current["VENCIDA"] == True].copy()
        if not vencidas_only.empty:
            cols_to_show = ["FACTURA", "USUARIO", "FECHA FACTURA", "DIAS_SIN_RADICAR", "RADICADO"]
            available_cols = [c for c in cols_to_show if c in vencidas_only.columns]
            vencidas_df = vencidas_only[available_cols].head(100)

    # By user aggregation
    by_user_df = None
    if df_current is not None and "USUARIO" in df_current.columns:
        user_agg = df_current.groupby("USUARIO").agg(
            TOTAL=("VENCIDA", "count"),
            VENCIDAS=("VENCIDA", "sum"),
        ).reset_index()
        user_agg["VENCIDAS"] = user_agg["VENCIDAS"].astype(int)
        user_agg["RADICADAS"] = user_agg["TOTAL"] - user_agg["VENCIDAS"]
        user_agg = user_agg.sort_values("VENCIDAS", ascending=False)
        by_user_df = user_agg

    executive_summary = {
        "total": total,
        "radicadas": radicadas,
        "vencidas": vencidas,
        "pct_radicado": pct_radicado,
        "pct_vencidas": pct_vencidas,
        "variation": _build_variation_block(total, prev_total),
        "variation_vencidas": _build_variation_block(vencidas, prev_vencidas),
    }

    return {
        "executive_summary": executive_summary,
        "vencidas_df": vencidas_df,
        "by_user": by_user_df,
    }


@st.cache_data(show_spinner=False, ttl=300)
def build_radicacion_report_cached(
        df_current: pd.DataFrame,
        df_previous: pd.DataFrame | None = None,
) -> dict:
    """Cached wrapper for radicación report generation."""
    return build_radicacion_report(df_current=df_current, df_previous=df_previous)


# ---------------------------------------------------------------------------
# General report (combines all modules)
# ---------------------------------------------------------------------------

def build_general_report(
        billing_report: dict | None = None,
        legalizations_report: dict | None = None,
        rips_report: dict | None = None,
        radicacion_report: dict | None = None,
        processes_report: dict | None = None,
) -> dict:
    """
    Combine all module reports into a single general report dict.

    Returns:
        dict with keys: billing, legalizations, rips, radicacion, processes
    """
    return {
        "billing": billing_report,
        "legalizations": legalizations_report,
        "rips": rips_report,
        "radicacion": radicacion_report,
        "processes": processes_report,
    }
