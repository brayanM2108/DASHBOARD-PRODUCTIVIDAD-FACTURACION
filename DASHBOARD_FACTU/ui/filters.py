"""
Filters and sidebar helpers
===========================
Reusable filtering components for the dashboard UI.
"""

import pandas as pd
import streamlit as st

from utils.date_helpers import get_default_date_range
from service.billers_service import get_billers_list


def render_date_filter(key_prefix=""):
    """
    Render an independent date range filter.
    """
    start_date_default, end_date_default = get_default_date_range(30)

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Desde",
            value=start_date_default,
            key=f"{key_prefix}_start_date"
        )
    with col2:
        end_date = st.date_input(
            "Hasta",
            value=end_date_default,
            key=f"{key_prefix}_end_date"
        )

    return start_date, end_date


def render_user_filter(df_facturadores, key_prefix=""):
    """
    Render an independent biller/user filter.
    """
    billers_list = get_billers_list(df_facturadores)

    if not billers_list:
        st.info("No hay facturadores disponibles.")
        return ['Todos']

    selected_users = st.multiselect(
        "Seleccionar Facturador",
        options=['Todos'] + billers_list,
        default=['Todos'],
        key=f"{key_prefix}_usuarios"
    )

    return selected_users


def _get_safe_date_bounds_from_df(df: pd.DataFrame | None, date_col: str | None) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Return safe (min_date, max_date) from a dataframe column, fallback to today."""
    if df is None or df.empty or not date_col or date_col not in df.columns:
        today = pd.Timestamp.now().normalize()
        return today, today

    series = pd.to_datetime(df[date_col], errors="coerce")
    min_value = series.min()
    max_value = series.max()

    if pd.isna(min_value) or pd.isna(max_value):
        today = pd.Timestamp.now().normalize()
        return today, today

    return min_value, max_value


def render_date_filter_with_bounds(
    min_date: pd.Timestamp,
    max_date: pd.Timestamp,
    key_prefix: str = "",
    label_start: str = "Fecha Inicio",
    label_end: str = "Fecha Fin",
):
    """Render a date range filter with explicit bounds."""
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            label_start,
            value=min_date,
            key=f"{key_prefix}_start_date",
        )
    with col2:
        end_date = st.date_input(
            label_end,
            value=max_date,
            key=f"{key_prefix}_end_date",
        )

    return start_date, end_date


def render_date_filter_from_df(
    df: pd.DataFrame | None,
    date_col: str | None,
    key_prefix: str = "",
    label_start: str = "Fecha Inicio",
    label_end: str = "Fecha Fin",
):
    """Render a date range filter using bounds derived from a dataframe column."""
    min_date, max_date = _get_safe_date_bounds_from_df(df, date_col)
    return render_date_filter_with_bounds(
        min_date,
        max_date,
        key_prefix=key_prefix,
        label_start=label_start,
        label_end=label_end,
    )


def render_single_select(label: str, options: list[str], key: str):
    """Render a simple selectbox with explicit options."""
    return st.selectbox(label, options, key=key)


def render_agreement_filter(agreement_list, key_prefix=""):
    """Render an agreement selector."""
    if not agreement_list:
        agreement_list = ["Todos"]
    return st.selectbox(
        "Convenio",
        agreement_list,
        key=f"{key_prefix}_convenio",
    )
