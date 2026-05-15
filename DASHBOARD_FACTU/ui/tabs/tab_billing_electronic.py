"""
Billing tab
===========
UI to visualize and analyze electronic billing productivity.
Uses only electronic billing data (USUARIO + VALOR TERCERO).
"""

import pandas as pd
import streamlit as st
from utils.excel_exporter import export_billing_report_cached
from config.settings import COLUMN_NAMES_BILLING
from data.validators import find_first_column_variant
from service.billing_electronic_service import (
    calculate_billing_productivity,
    filter_billing,
    get_billing_with_user,
    prepare_electronic_billing_df_cached,

)
from service.report_service import build_billing_report_cached
from ui.components import (
    create_download_button,
    create_excel_download_button,
    show_dataframe,
    show_info_message,
)
from ui.filters import (
    render_agreement_filter,
    render_date_filter_from_df,
    render_single_select,
)
from ui.visualizations import (
    plot_billing_electronic_value_by_user,
    plot_billing_electronic_records_by_user,
    plot_billing_electronic_records_by_date,
)

ALL_OPTION = "Todos"
KEY_PREFIX = "billing_v2"


def _find_user_column(df: pd.DataFrame) -> str | None:
    return find_first_column_variant(df, COLUMN_NAMES_BILLING.get("usuario", []))

def _find_agreement_column(df: pd.DataFrame) -> str | None:
    return find_first_column_variant(df, COLUMN_NAMES_BILLING.get("convenio", []))

def _find_date_column(df: pd.DataFrame) -> str | None:
    return find_first_column_variant(df, COLUMN_NAMES_BILLING.get("fecha", []))


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
    st.subheader("Productividad Facturación")
    
    e_billing_df = prepare_electronic_billing_df_cached(e_billing_df)
    if e_billing_df is None or e_billing_df.empty:
        show_info_message("No hay datos de facturación electrónica válidos para procesar.")
        return

    user_col = _find_user_column(e_billing_df)
    date_col = _find_date_column(e_billing_df)
    agreement_col = _find_agreement_column(e_billing_df)

    start_date, end_date = render_date_filter_from_df(
        e_billing_df,
        date_col,
        key_prefix=KEY_PREFIX,
        label_start="Fecha Inicio",
        label_end="Fecha Fin",
    )

    users_list = [ALL_OPTION]
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
        users_list = [ALL_OPTION] + sorted(usuarios_unicos)

    agreement_list = [ALL_OPTION]
    if agreement_col and agreement_col in e_billing_df.columns:
        agrements_unicos = (
            e_billing_df[agreement_col]
            .dropna()
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
            .unique()
            .tolist()
        )
        agreement_list = [ALL_OPTION] + sorted(agrements_unicos)

    col3, col4 = st.columns(2)
    with col3:
        agremeent_sel = render_agreement_filter(
            agreement_list,
            key_prefix=KEY_PREFIX,
        )
    selected_agreement = None if agremeent_sel == ALL_OPTION else agremeent_sel

    with col4:
        usuario_sel = render_single_select(
            "Usuario",
            users_list,
            key=f"{KEY_PREFIX}_usuario",
        )
    selected_users = None if usuario_sel == ALL_OPTION else [usuario_sel]

    filtered_e_billing_df = filter_billing(
        e_billing_df,
        start_date,
        end_date,
        selected_users=selected_users,
        selected_agreement = selected_agreement
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

    if selected_users and result_user_col in productivity_base_df.columns:
        productivity_base_df = productivity_base_df[
            productivity_base_df[result_user_col].isin(selected_users)
        ]

    if (
            report_by_user_df is not None
            and not report_by_user_df.empty
            and selected_users
            and result_user_col in report_by_user_df.columns
    ):
        report_by_user_df = report_by_user_df[
            report_by_user_df[result_user_col].isin(selected_users)
        ]

    period_label = f"{start_date} - {end_date}"
    billing_report = build_billing_report_cached(
        df_current=productivity_base_df,
        df_previous=None,
        by_user_df=report_by_user_df,
    )
    billing_excel = export_billing_report_cached(billing_report, period_label=period_label)

    filename_suffix = f"_{usuario_sel}" if selected_users else ""
    filename = f"INFORME_PRODUCTIVIDAD_FACTURACION_{filename_suffix}.xlsx"
    
    create_excel_download_button(
        billing_excel,
        filename=filename,
        label=" Descargar informe de productividad (Excel)",
    )

    metrics = calculate_billing_productivity(productivity_base_df)

    if "VALOR TERCERO" in productivity_base_df.columns:
        total_valor = pd.to_numeric(
            productivity_base_df["VALOR TERCERO"], errors="coerce"
        ).fillna(0).sum()
    else:
        total_valor = 0.0

    total_registros = len(productivity_base_df)


    c1, c2 = st.columns(2)
    with c1:
        st.metric("Total de Registros", f"{total_registros:,}")
    with c2:
        st.metric("Total Valor Tercero", f"${total_valor:,.0f}")

    st.subheader(" Valor Facturado por Usuario")
    if report_by_user_df is None or report_by_user_df.empty:
        show_info_message("No hay datos para graficar por usuario.")
    else:
        df_valor = report_by_user_df.copy()
        plot_billing_electronic_value_by_user(df_valor, result_user_col)

        df_valor_show = df_valor.copy()
        df_valor_show["COUNT"] = pd.to_numeric(df_valor_show["COUNT"], errors="coerce").fillna(0)
        st.dataframe(df_valor_show.style.format({"COUNT": "${:,.0f}"}), width="stretch")

    st.subheader(" Cantidad de Registros por Usuario")
    df_registros = plot_billing_electronic_records_by_user(productivity_base_df, result_user_col)
    if df_registros is not None and not df_registros.empty:
        st.dataframe(df_registros, width="stretch")



    st.subheader(" Valor Facturado por Fecha")
    df_fecha_registros = plot_billing_electronic_records_by_date(metrics.get("by_date_dual"))
    if df_fecha_registros is not None and not df_fecha_registros.empty:
        st.dataframe(df_fecha_registros.style.format({"VALOR_TERCERO": "${:,.0f}"}), width="stretch")
