"""
Filters and sidebar helpers
===========================
Reusable filtering components for the dashboard UI.
"""

from datetime import date, timedelta

import pandas as pd
import streamlit as st


def render_date_filter(key_prefix=""):
    """
    Render an independent date range filter.
    """
    today = date.today()
    start_date_default = today - timedelta(days=30)
    end_date_default = today

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
    if df_facturadores is not None and not df_facturadores.empty and "NOMBRE" in df_facturadores.columns:
        billers_list = sorted(
            df_facturadores["NOMBRE"]
            .dropna()
            .astype(str)
            .str.strip()
            .str.upper()
            .unique()
        )
    else:
        billers_list = []

    if not billers_list:
        st.info("No hay facturadores disponibles.")
        return ['Todos']

    selected_users = st.selectbox(
        "Seleccionar Usuario",
        options=['Todos'] + billers_list,
        key=f"{key_prefix}_usuarios"
    )

    return selected_users


def render_role_user_filter(billers_df, key_prefix=""):
    """
    Multi-select user filter with options sorted by ROL (ANALISTAS / AUXILIARES).
    """
    if billers_df is None or billers_df.empty:
        st.info("No hay datos de facturadores.")
        return ["Todos"]

    items = ["Todos"]
    if "ROL" in billers_df.columns and "NOMBRE" in billers_df.columns:
        grouped = billers_df.dropna(subset=["NOMBRE", "ROL"]).copy()
        grouped["NOMBRE"] = grouped["NOMBRE"].astype(str).str.strip()
        grouped["ROL"] = grouped["ROL"].astype(str).str.strip().str.upper()

        for role in sorted(grouped["ROL"].unique()):
            users_in_role = sorted(grouped[grouped["ROL"] == role]["NOMBRE"].unique())
            for u in users_in_role:
                items.append(u)

    default = st.session_state.get(f"{key_prefix}_usuario", ["Todos"])
    selected = st.multiselect(
        "Facturador",
        options=items,
        default=default if all(o in items for o in default) else ["Todos"],
        key=f"{key_prefix}_usuario",
    )

    if "Todos" in selected or not selected:
        return ["Todos"]

    return selected


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


def _safe_min_date(df: pd.DataFrame, date_col: str | None) -> pd.Timestamp:
    if date_col and date_col in df.columns:
        min_value = pd.to_datetime(df[date_col], errors="coerce").min()
        if pd.notna(min_value):
            return min_value
    return pd.Timestamp.now()


def _safe_max_date(df: pd.DataFrame, date_col: str | None) -> pd.Timestamp:
    if date_col and date_col in df.columns:
        max_value = pd.to_datetime(df[date_col], errors="coerce").max()
        if pd.notna(max_value):
            return max_value
    return pd.Timestamp.now()
