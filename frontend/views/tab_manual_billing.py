"""Manual Billing Tab — API-driven CRUD + charts. GolemanTheme design."""

import traceback
from datetime import date

import pandas as pd
import streamlit as st

from frontend.components.visualizations import (
    plot_manual_bar,
    plot_manual_pie,
    plot_manual_trend,
    clear_viz_filter,
    any_viz_filter_active,
)
from frontend.services.manual_billing_service import ManualBillingFrontendService
from frontend.services.process_config_service import ProcessConfigFrontendService
from frontend.components.components import (
    show_error_message,
    show_warning_message,
    show_success_message,
)
from ui.goleman_theme import GolemanTheme

_VIZ_KEY = "manual_billing"


def _section_title(label: str) -> None:
    st.markdown(f'<div class="g-section-title">{label}</div>', unsafe_allow_html=True)


def _render_kpis(kpis: dict):
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Total Registros", f"{kpis.get('total_records', 0):,}")
    with k2:
        st.metric("Total Cantidad", f"{kpis.get('total_quantity', 0.0):,.0f}")
    with k3:
        st.metric("Personas", f"{kpis.get('unique_people', 0):,}")
    with k4:
        st.metric("Tipos de Procesos", f"{kpis.get('unique_processes', 0):,}")


def _render_charts(chart_data: dict):
    if any_viz_filter_active(_VIZ_KEY):
        if st.button("Limpiar filtro", key="clear_mb_filter", use_container_width=True):
            clear_viz_filter(_VIZ_KEY)
            st.rerun()

    col_left, col_right = st.columns([2, 1])
    with col_left:
        _section_title("Cantidad por Persona")
        plot_manual_bar(chart_data.get("bar_by_person"), view_key=_VIZ_KEY)

    with col_right:
        pie_df = chart_data.get("pie_distribution")
        if pie_df is not None and not pie_df.empty:
            mode = chart_data.get("pie_mode", "person")
            label = "Distribucion por Persona" if mode == "person" else "Cantidad por Proceso"
            _section_title(label)
            plot_manual_pie(pie_df, mode, view_key=_VIZ_KEY)

    _section_title("Tendencia Temporal")
    plot_manual_trend(chart_data.get("time_trend"), view_key=_VIZ_KEY)


def _render_records_table(service: ManualBillingFrontendService, records, df: pd.DataFrame):
    with st.expander("Ver todos los registros", expanded=False):
        st.dataframe(df, use_container_width=True)

        if records:
            opts = {}
            for r in records:
                label = f"ID {r.id} \u2014 {r.fecha} \u2014 {r.nombre} \u2014 {r.proceso} ({r.cantidad})"
                opts[label] = r.id
            selected_label = st.selectbox(
                "Seleccionar registro para eliminar",
                options=list(opts.keys()),
                key="mb_delete_select",
            )
            if st.button("Eliminar seleccionado", key="mb_delete_btn"):
                confirm_key = "_mb_confirm_delete"
                if st.session_state.get(confirm_key) != selected_label:
                    st.session_state[confirm_key] = selected_label
                    show_warning_message(
                        f"Presiona nuevamente 'Eliminar' para confirmar la eliminacion de ID {opts[selected_label]}"
                    )
                    st.rerun()
                else:
                    try:
                        service.delete_record(opts[selected_label])
                        show_success_message("Registro eliminado.")
                        st.session_state["_mb_refresh"] = True
                        st.session_state.pop(confirm_key, None)
                        st.rerun()
                    except Exception as e:
                        show_error_message(f"Error al eliminar: {e}")

    if st.session_state.get("_mb_confirm_delete") and st.button("Cancelar", key="mb_cancel_delete"):
        st.session_state.pop("_mb_confirm_delete", None)
        st.rerun()


_DEFAULT_PROCESS_OPTIONS = [
    "AUDITAR CUENTAS",
    "RADICAR CUENTAS",
    "DESCARGAR SOPORTES",
    "VALIDAR RIPS",
    "UNIFICAR SOPORTES",
    "DESCARGAR AUTORIZACIONES",
]


def _get_process_options() -> list[str]:
    try:
        service = ProcessConfigFrontendService()
        config = service.get_config()
        names = [p.get("name", "") for p in config.get("processes", []) if p.get("name")]
        if names:
            return names
    except Exception:
        pass
    return _DEFAULT_PROCESS_OPTIONS


def _render_registration_form(service: ManualBillingFrontendService):
    with st.form("form_new_process", clear_on_submit=True):
        col_fecha, col_proceso, col_cantidad = st.columns(3)
        with col_fecha:
            fecha = st.date_input("Fecha", value=date.today())
        with col_proceso:
            proceso = st.selectbox("Proceso", options=_get_process_options(), key="mb_proceso_sel")
        with col_cantidad:
            cantidad = st.number_input("Cantidad", min_value=1, step=1)
        observacion = st.text_area("Observacion (opcional)", max_chars=500)
        submitted = st.form_submit_button("Registrar", type="primary")
        if submitted:
            if not proceso:
                show_error_message("El proceso es obligatorio.")
            else:
                try:
                    obs = observacion.strip() or None
                    service.create_record(fecha, proceso.strip(), int(cantidad), observacion=obs)
                    show_success_message(f"Registro creado: {proceso.strip()}")
                    st.session_state["_mb_refresh"] = True
                    st.rerun()
                except Exception as e:
                    show_error_message(f"Error al crear registro: {e}")
                    if st.checkbox("Ver detalle tecnico", key="mb_reg_err_detail"):
                        st.code(traceback.format_exc())


def render_tab_manual_billing():
    service = ManualBillingFrontendService()

    if st.session_state.get("_mb_refresh"):
        st.session_state.pop("_mb_records", None)
        st.session_state["_mb_refresh"] = False

    if "_mb_records" not in st.session_state:
        try:
            records = service.get_records()
            st.session_state["_mb_records"] = records
        except Exception as e:
            show_error_message(f"Error al cargar datos: {e}")
            return

    records = st.session_state["_mb_records"]

    # ── Header: title + button (orange) ──
    st.markdown(f"""
    <style>
    [data-testid="stMainBlockContainer"] button[kind="primary"] {{
        background: {GolemanTheme.ORANGE} !important;
        color: {GolemanTheme.WHITE} !important;
        border: none !important;
        border-radius: 10px !important;
        height: 38px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        letter-spacing: .02em !important;
        box-shadow: 0 4px 14px rgba(249,120,56,.35) !important;
        transition: background .15s ease !important;
    }}
    [data-testid="stMainBlockContainer"] button[kind="primary"]:hover {{
        background: #e86a2b !important;
        box-shadow: 0 6px 20px rgba(249,120,56,.45) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    c_title, c_btn = st.columns([3, 1])
    with c_title:
        st.markdown(f"""
        <div style="font-size:20px;font-weight:700;color:{GolemanTheme.NAVY}">Procesos Administrativos</div>
        <div style="font-size:12px;color:{GolemanTheme.MUTED};margin-top:2px">Monitorea la productividad y registra nuevos procesos administrativos.</div>
        """, unsafe_allow_html=True)
    with c_btn:
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        if st.button(
            "+ Nuevo registro",
            use_container_width=True,
            type="primary",
            key="mb_toggle_form",
        ):
            st.session_state["_mb_show_form"] = not st.session_state.get("_mb_show_form", False)
            st.rerun()

    if not records:
        st.markdown(
            GolemanTheme.info_banner(
                "No hay registros. Usa el formulario de registro para agregar datos.",
                kind="info",
            ),
            unsafe_allow_html=True,
        )
        _render_registration_form(service)
        return

    df = service.to_dataframe(records)

    if st.session_state.get("_mb_show_form", False):
        _render_registration_form(service)

    kpis = service.get_kpis_from_df(df)
    _section_title("Metricas del periodo")
    _render_kpis(kpis)

    chart_data = service.build_chart_datasets(df)
    _render_charts(chart_data)

    _section_title("Registros")
    _render_records_table(service, records, df)


