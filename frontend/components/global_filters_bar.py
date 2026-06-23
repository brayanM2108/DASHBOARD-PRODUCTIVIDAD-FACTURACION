"""
Global Filters Bar — Sección independiente con filtros globales.
CSS via GolemanTheme.global_filters.
"""

import pandas as pd
import streamlit as st

from frontend.components.filters import render_role_user_filter


def _derive_date_bounds() -> tuple:
    min_date = pd.Timestamp("2020-01-01").date()
    max_date = pd.Timestamp.now().date()
    date_cols = ("FECHA", "fecha", "FECHA_SERVICIO", "FECHA FACTURA", "FECHA_COMPLETADO_RIPS")

    module_keys = [
        "legalizations_df",
        "rips_df",
        "electronic_billing_df",
        "administrative_processes_df",
    ]
    for key in module_keys:
        df = st.session_state.get(key)
        if df is None or df.empty:
            continue
        for col in date_cols:
            if col in df.columns:
                parsed = pd.to_datetime(df[col], errors="coerce").dropna()
                if not parsed.empty:
                    min_date = min(min_date, parsed.min().date())
                    max_date = max(max_date, parsed.max().date())
                break
    return min_date, max_date


def render_global_filters_bar() -> None:
    user = st.session_state.get("user", {})
    role = user.get("role") if user else None
    is_admin = role in ("ADMIN", "SUPERVISOR")

    min_date, max_date = _derive_date_bounds()

    with st.container(key="gf_bar"):
        cols = st.columns([2, 2, 3, 2], gap="small")

        with cols[0]:
            st.session_state["global_start_date"] = st.date_input(
                "Fecha inicio",
                value=st.session_state.get("global_start_date", min_date),
                min_value=min_date,
                max_value=max_date,
                key="gf_start",
            )

        with cols[1]:
            st.session_state["global_end_date"] = st.date_input(
                "Fecha fin",
                value=st.session_state.get("global_end_date", max_date),
                min_value=min_date,
                max_value=max_date,
                key="gf_end",
            )

        with cols[2]:
            if is_admin:
                selected_user = render_role_user_filter(
                    st.session_state.get("billers_df"),
                    key_prefix="gf",
                )
                st.session_state["global_user"] = selected_user
            else:
                st.markdown(
                    '<div style="display:flex;align-items:center;height:100%;'
                    'padding-top:22px;font-size:13px;color:#1A2A45;font-weight:500">'
                    'Viendo tus metricas</div>',
                    unsafe_allow_html=True,
                )
                st.session_state["global_user"] = ["Todos"]

        with cols[3]:
            if st.button(
                "Aplicar filtros",
                type="primary",
                key="gf_apply",
                use_container_width=True,
            ):
                st.rerun()
