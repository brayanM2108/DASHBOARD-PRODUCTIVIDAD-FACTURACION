"""
Legalizations tab
=================
UI to visualize and analyze PPL and agreements legalizations.

User filter lives at the top level so it applies to both PPL and
Agreements sub-tabs simultaneously, and drives the Excel export.
"""

import pandas as pd
import streamlit as st

from config.settings import COLUMN_NAMES, COLUMN_NAMES_LEGALIZATIONS
from data.validators import find_first_column_variant
from service.legalizations_service import (
    calculate_legalizations_productivity_cached,
    filter_legalizations,
)
from service.report_service import build_legalizations_report_cached
from utils.excel_exporter import export_legalizations_report_cached
from ui.components import create_download_button, show_dataframe, show_info_message
from ui.filters import render_date_filter_from_df, render_single_select
from ui.visualizations import plot_productivity_charts

ALL_OPTION = "Todos"


# ---------------------------------------------------------------------------
# User options helper — merges users from both datasets
# ---------------------------------------------------------------------------

def _build_combined_user_options(
        ppl_df: pd.DataFrame | None,
        agreements_df: pd.DataFrame | None,
) -> list[str]:
    """
    Return sorted unique users from PPL and Agreements combined.
    This ensures the selector covers users that may appear in only one dataset.
    """
    users: set[str] = set()

    for df in (ppl_df, agreements_df):
        if df is None or df.empty:
            continue
        user_col = find_first_column_variant(df, COLUMN_NAMES["usuario"])
        if user_col and user_col in df.columns:
            users.update(df[user_col].dropna().astype(str).unique().tolist())

    return [ALL_OPTION] + sorted(users)


# ---------------------------------------------------------------------------
# Period label builder for the Excel filename / cover
# ---------------------------------------------------------------------------

def _period_label(start_date, end_date) -> str:
    return f"{start_date.strftime('%d/%m/%Y')} – {end_date.strftime('%d/%m/%Y')}"


# ---------------------------------------------------------------------------
# Main tab renderer
# ---------------------------------------------------------------------------

def render_tab_legalizations():
    """Render legalizations tab with shared filters and PPL / Agreements sub-tabs."""
    st.header(" Legalizaciones")

    ppl_df = st.session_state.get("ppl_legalizations_df")
    agreements_df = st.session_state.get("agreement_legalizations_df")

    if (ppl_df is None or ppl_df.empty) and (agreements_df is None or agreements_df.empty):
        show_info_message("No hay datos de legalizaciones. Carga un archivo en la sección de carga.")
        return

    # ------------------------------------------------------------------
    # Shared filters — applied to BOTH sub-tabs and the Excel export
    # ------------------------------------------------------------------
    st.subheader("Filtros")

    # Date range — derive bounds from whichever dataset is available
    reference_df = ppl_df if ppl_df is not None and not ppl_df.empty else agreements_df
    date_col_ref = find_first_column_variant(reference_df, COLUMN_NAMES_LEGALIZATIONS["fecha"])

    start_date, end_date = render_date_filter_from_df(
        reference_df,
        date_col_ref,
        key_prefix="leg",
        label_start="Fecha Inicio",
        label_end="Fecha Fin",
    )

    # User selector — built from the union of both datasets
    user_options = _build_combined_user_options(ppl_df, agreements_df)
    selected_user = render_single_select("Usuario", user_options, key="leg_user")
    selected_users = None if selected_user == ALL_OPTION else [selected_user]

    # ------------------------------------------------------------------
    # Apply shared filters to both datasets
    # ------------------------------------------------------------------
    filtered_ppl_df = filter_legalizations(ppl_df, start_date, end_date, selected_users)
    filtered_agreements_df = filter_legalizations(agreements_df, start_date, end_date, selected_users)

    # ------------------------------------------------------------------
    # Excel download — uses already-filtered dataframes
    # ------------------------------------------------------------------
    st.divider()

    # Previous period inputs (collapsed to keep UI clean)
    with st.expander(" Comparar con período anterior (opcional)"):
        col3, col4 = st.columns(2)
        with col3:
            prev_start = st.date_input("Inicio período anterior", key="leg_prev_start")
        with col4:
            prev_end = st.date_input("Fin período anterior", key="leg_prev_end")

        prev_ppl_df = filter_legalizations(ppl_df, prev_start, prev_end, selected_users)
        prev_agreements_df = filter_legalizations(agreements_df, prev_start, prev_end, selected_users)

    period = _period_label(start_date, end_date)
    filename_suffix = f"_{selected_user}" if selected_users else ""
    filename = f"informe_legalizaciones{filename_suffix}.xlsx"

    report = build_legalizations_report_cached(
        ppl_current=filtered_ppl_df,
        agreements_current=filtered_agreements_df,
        ppl_previous=prev_ppl_df if "prev_ppl_df" in dir() else None,
        agreements_previous=prev_agreements_df if "prev_agreements_df" in dir() else None,
    )
    excel_bytes = export_legalizations_report_cached(report, period_label=period)

    st.download_button(
        label=" Descargar informe de productividad (Excel)",
        data=excel_bytes,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="leg_download",
    )

    st.divider()

    # ------------------------------------------------------------------
    # Sub-tabs — receive already-filtered dataframes
    # ------------------------------------------------------------------
    tab_ppl, tab_convenios = st.tabs([" PPL", " Convenios"])

    with tab_ppl:
        _render_ppl_section(filtered_ppl_df)

    with tab_convenios:
        _render_agreements_section(filtered_agreements_df)


# ---------------------------------------------------------------------------
# Sub-section renderers — no filters here, data arrives pre-filtered
# ---------------------------------------------------------------------------

def _render_ppl_section(ppl_df: pd.DataFrame | None) -> None:
    """Render PPL section. Receives already-filtered dataframe."""
    st.subheader("Legalizaciones PPL")

    if ppl_df is None or ppl_df.empty:
        show_info_message("No hay datos de legalizaciones PPL para los filtros seleccionados.")
        return

    metrics = calculate_legalizations_productivity_cached(ppl_df)
    plot_productivity_charts(metrics, tipo="Legalizaciones PPL")


def _render_agreements_section(agreements_df: pd.DataFrame | None) -> None:
    """Render Agreements section. Receives already-filtered dataframe."""
    st.subheader("Legalizaciones Convenios")

    if agreements_df is None or agreements_df.empty:
        show_info_message("No hay datos de legalizaciones de Convenios para los filtros seleccionados.")
        return

    metrics = calculate_legalizations_productivity_cached(agreements_df, category="Convenios")
    plot_productivity_charts(metrics, tipo="Legalizaciones Convenios")
