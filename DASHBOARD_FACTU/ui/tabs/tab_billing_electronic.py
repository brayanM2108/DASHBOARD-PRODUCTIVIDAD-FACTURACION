"""
Billing tab
===========
UI to visualize and analyze electronic billing productivity.
Uses only electronic billing data (USUARIO + VALOR TERCERO).
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config.settings import COLUMN_NAMES_BILLING
from data.validators import find_first_column_variant
from service.billing_electronic_service import (
    calculate_billing_productivity,
    filter_billing,
    get_billing_with_user,
)
from service.report_service import build_billing_report
from ui.components import (
    create_download_button,
    create_excel_download_button,
    show_dataframe,
    show_info_message,
)
from ui.visualizations import plot_bar_chart
from utils.excel_exporter import export_billing_report

ALL_OPTION = "Todos"
KEY_PREFIX = "billing_v2"


def _normalize_columns_upper(df: pd.DataFrame) -> pd.DataFrame:
    copy_df = df.copy()
    copy_df.columns = copy_df.columns.astype(str).str.strip().str.upper()
    return copy_df


def _find_user_column(df: pd.DataFrame) -> str | None:
    return find_first_column_variant(df, COLUMN_NAMES_BILLING.get("usuario", []))


def _find_date_column(df: pd.DataFrame) -> str | None:
    return find_first_column_variant(df, COLUMN_NAMES_BILLING.get("fecha", []))


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


def _plot_dual_trend(by_date_dual: pd.DataFrame | None) -> None:
    """Bar + line chart: registros vs valor tercero by date."""
    if by_date_dual is None or by_date_dual.empty:
        show_info_message("No hay tendencia por fecha para los filtros actuales.")
        return

    fig = go.Figure()

    fig.add_bar(
        x=by_date_dual["DATE"],
        y=by_date_dual["REGISTROS"],
        name="Registros",
        yaxis="y1",
    )

    fig.add_scatter(
        x=by_date_dual["DATE"],
        y=by_date_dual["VALOR_TERCERO"],
        name="Valor Tercero",
        mode="lines+markers",
        yaxis="y2",
    )

    fig.update_layout(
        title="Tendencia diaria: Registros vs Valor Tercero",
        xaxis=dict(title="Fecha"),
        yaxis=dict(title="Registros"),
        yaxis2=dict(
            title="Valor Tercero",
            overlaying="y",
            side="right",
        ),
        legend=dict(orientation="h"),
    )

    st.plotly_chart(fig, width="stretch")


def render_tab_billing_electronic():
    """Render the billing V2 tab."""
    st.header("Facturación V2")
    render_billing_electronic_section()


def render_billing_electronic_section():
    """Render billing section based only on electronic billing."""
    e_billing_df = st.session_state.get("electronic_billing_df")

    if e_billing_df is None or e_billing_df.empty:
        show_info_message("No hay datos de facturación electrónica. Carga un archivo en la sección de carga.")
        return

    e_billing_df = _normalize_columns_upper(e_billing_df)

    user_col = _find_user_column(e_billing_df)
    date_col = _find_date_column(e_billing_df)

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Fecha Inicio",
            value=_safe_min_date(e_billing_df, date_col),
            key=f"{KEY_PREFIX}_start_date",
        )
    with col2:
        end_date = st.date_input(
            "Fecha Fin",
            value=_safe_max_date(e_billing_df, date_col),
            key=f"{KEY_PREFIX}_end_date",
        )

    usuarios_lista = [ALL_OPTION]
    if user_col and user_col in e_billing_df.columns:
        usuarios_unicos = (
            e_billing_df[user_col]
            .dropna()
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
            .unique()
            .tolist()
        )
        usuarios_lista = [ALL_OPTION] + sorted(usuarios_unicos)

    usuario_sel = st.selectbox(
        "Usuario",
        usuarios_lista,
        key=f"{KEY_PREFIX}_usuario",
    )
    usuarios_seleccionados = None if usuario_sel == ALL_OPTION else [usuario_sel]

    filtered_e_billing_df = filter_billing(
        e_billing_df,
        start_date,
        end_date,
        selected_users=usuarios_seleccionados,
    )

    if filtered_e_billing_df is None or filtered_e_billing_df.empty:
        show_info_message("No hay datos que coincidan con los filtros seleccionados.")
        return

    result = get_billing_with_user(
        billing_df=None,
        electronic_billing_df=filtered_e_billing_df,
        billers_df=None,
    )

    if result["error"]:
        st.warning(result["error"])
        return

    productivity_base_df = result["billing_with_user_df"]
    report_by_user_df = result["billing_by_user_df"]
    result_user_col = result["user_column"]

    if usuarios_seleccionados and result_user_col in productivity_base_df.columns:
        productivity_base_df = productivity_base_df[
            productivity_base_df[result_user_col].isin(usuarios_seleccionados)
        ]

    if (
            report_by_user_df is not None
            and not report_by_user_df.empty
            and usuarios_seleccionados
            and result_user_col in report_by_user_df.columns
    ):
        report_by_user_df = report_by_user_df[
            report_by_user_df[result_user_col].isin(usuarios_seleccionados)
        ]

    period_label = f"{start_date} - {end_date}"
    billing_report = build_billing_report(
        df_current=productivity_base_df,
        df_previous=None,
        by_user_df=report_by_user_df,
    )
    billing_excel = export_billing_report(billing_report, period_label=period_label)

    create_excel_download_button(
        billing_excel,
        filename=f"billing_v2_productivity_{start_date}_{end_date}.xlsx",
        label="📥 Descargar informe de productividad (Excel)",
    )

    # ---- KPIs duales solicitados ----
    metrics = calculate_billing_productivity(productivity_base_df)

    # ---- Por usuario (valor tercero) ----
    if "VALOR TERCERO" in productivity_base_df.columns:
        total_valor = pd.to_numeric(
            productivity_base_df["VALOR TERCERO"], errors="coerce"
        ).fillna(0).sum()
    else:
        total_valor = 0.0

    total_registros = len(productivity_base_df)

    st.subheader("📌 Indicadores principales")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Total de Registros", f"{total_registros:,}")
    with c2:
        st.metric("Total Valor Tercero", f"${total_valor:,.2f}")

    # ---- Gráfica 1: valor facturado por usuario ----
    st.subheader("📈 Valor Facturado por Usuario")
    if report_by_user_df is None or report_by_user_df.empty:
        show_info_message("No hay datos para graficar por usuario.")
    else:
        df_valor = report_by_user_df.copy()
        plot_bar_chart(
            df_valor,
            x_col=result_user_col,
            y_col="COUNT",
            title="Valor Facturado por Usuario",
            sort_key="billing_v2_user_bar",
        )

        # Tabla con formato moneda
        df_valor_show = df_valor.copy()
        df_valor_show["COUNT"] = pd.to_numeric(df_valor_show["COUNT"], errors="coerce").fillna(0)
        st.dataframe(
            df_valor_show.style.format({"COUNT": "${:,.2f}"}),
            width="stretch",
        )

    # ---- Gráfica 2: cantidad de registros por usuario (debajo) ----
    st.subheader("📊 Cantidad de Registros por Usuario")
    if productivity_base_df is None or productivity_base_df.empty:
        show_info_message("No hay datos para graficar registros por usuario.")
    else:
        df_registros = (
            productivity_base_df
            .groupby(result_user_col, as_index=False)
            .size()
            .rename(columns={"size": "REGISTROS"})
            .sort_values("REGISTROS", ascending=False)
        )

        plot_bar_chart(
            df_registros,
            x_col=result_user_col,
            y_col="REGISTROS",
            title="Cantidad de Registros por Usuario",
            sort_key="billing_v2_records_bar",
        )

        st.dataframe(df_registros, width="stretch")

    with st.expander("📊 Ver datos detallados", expanded=False):
        show_dataframe(filtered_e_billing_df, title="Datos de Facturacion Electronica Filtrados")
        create_download_button(
            filtered_e_billing_df,
            "facturacion_electronica_filtrada.csv",
        )
