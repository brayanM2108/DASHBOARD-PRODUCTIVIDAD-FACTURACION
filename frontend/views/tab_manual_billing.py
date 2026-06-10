"""Manual Billing Tab — API-driven CRUD + charts."""

import traceback
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from frontend.services.manual_billing_service import ManualBillingFrontendService
from frontend.components.filters import render_date_filter_with_bounds, render_single_select
from frontend.components.components import (
    show_error_message,
    show_warning_message,
    show_success_message,
    create_excel_download_button,
)

ALL_OPTION = "Todos"

try:
    from backend.app.services.report_service import build_processes_report_cached
    from backend.app.etl.excel_exporter import export_processes_report_cached

    _EXCEL_AVAILABLE = True
except ImportError:
    _EXCEL_AVAILABLE = False


def _safe_date_str(d):
    if d is None:
        return ""
    try:
        return d.isoformat()
    except Exception:
        return str(d)


def _get_date_bounds(records):
    fechas = []
    for r in records:
        try:
            fechas.append(pd.Timestamp(r.fecha))
        except Exception:
            pass
    if fechas:
        return min(fechas).date(), max(fechas).date()
    today = date.today()
    return today, today


def _render_registration_form(service: ManualBillingFrontendService):
    with st.expander("➕ Registrar nuevo proceso", expanded=False):
        with st.form("form_new_process", clear_on_submit=True):
            col_fecha, col_proceso, col_cantidad = st.columns(3)
            with col_fecha:
                fecha = st.date_input("Fecha", value=date.today())
            with col_proceso:
                proceso = st.text_input("Proceso", max_chars=255)
            with col_cantidad:
                cantidad = st.number_input("Cantidad", min_value=1, step=1)
            observacion = st.text_area("Observación (opcional)", max_chars=500)
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
                        if st.checkbox("Ver detalle técnico", key="mb_reg_err_detail"):
                            st.code(traceback.format_exc())


def _render_filters(df: pd.DataFrame):
    try:
        fe = pd.to_datetime(df["FECHA"], errors="coerce").dropna()
        if not fe.empty:
            min_date, max_date = fe.min().date(), fe.max().date()
        else:
            today = date.today()
            min_date = max_date = today
    except Exception:
        today = date.today()
        min_date = max_date = today

    start_date, end_date = render_date_filter_with_bounds(
        min_date, max_date, key_prefix="manual_proc",
        label_start="Fecha inicio", label_end="Fecha fin",
    )

    if start_date and end_date and end_date < start_date:
        show_warning_message("La fecha fin es anterior a la fecha inicio. Ajustando.")
        end_date = start_date
        st.session_state["manual_proc_end_date"] = end_date

    people = [ALL_OPTION] + sorted(df["NOMBRE"].dropna().astype(str).unique().tolist())
    processes = [ALL_OPTION] + sorted(df["PROCESO"].dropna().astype(str).unique().tolist())

    c1, c2 = st.columns(2)
    with c1:
        selected_person = render_single_select("Persona", people, key="manual_proc_person")
    with c2:
        selected_process = render_single_select("Proceso", processes, key="manual_proc_process")

    return start_date, end_date, selected_person, selected_process


def _render_kpis(kpis: dict):
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Registros", kpis.get("total_records", 0))
    with m2:
        qty = kpis.get("total_quantity", 0.0)
        try:
            st.metric("Total Cantidad", f"{qty:,.0f}")
        except Exception:
            st.metric("Total Cantidad", qty)
    with m3:
        st.metric("Personas", kpis.get("unique_people", 0))
    with m4:
        st.metric("Tipos de Procesos", kpis.get("unique_processes", 0))


def _render_charts(chart_data: dict):
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.subheader("Cantidad por Persona")
        bar_df = chart_data.get("bar_by_person")
        if bar_df is None or bar_df.empty:
            st.info("No hay datos para el gráfico de barras.")
        else:
            try:
                fig = px.bar(bar_df, x="NOMBRE", y="CANTIDAD", color="CANTIDAD", color_continuous_scale="Blues")
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                show_warning_message(f"Error en gráfico de barras: {e}")

    with col_right:
        pie_df = chart_data.get("pie_distribution")
        if pie_df is None or pie_df.empty:
            st.info("No hay datos para el gráfico de torta.")
        else:
            try:
                if chart_data.get("pie_mode") == "person":
                    st.subheader("Distribución por Persona")
                    fig = px.pie(pie_df, values="CANTIDAD", names="NOMBRE", hole=0.4)
                else:
                    st.subheader("Cantidad por Proceso")
                    fig = px.pie(pie_df, values="CANTIDAD", names="PROCESO", hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                show_warning_message(f"Error en gráfico de torta: {e}")

    st.subheader("Tendencia Temporal")
    trend_df = chart_data.get("time_trend")
    if trend_df is None or trend_df.empty:
        st.info("No hay datos para la tendencia temporal.")
    else:
        try:
            fig = px.line(trend_df, x="FECHA", y="CANTIDAD", markers=True)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            show_warning_message(f"Error en tendencia: {e}")


def _render_records_table(service: ManualBillingFrontendService, records, filtered_df: pd.DataFrame):
    with st.expander("📋 Ver todos los registros", expanded=False):
        st.dataframe(filtered_df, use_container_width=True)

        if records:
            opts = {}
            for r in records:
                label = f"ID {r.id} — {r.fecha} — {r.nombre} — {r.proceso} ({r.cantidad})"
                opts[label] = r.id
            selected_label = st.selectbox("Seleccionar registro para eliminar", options=list(opts.keys()), key="mb_delete_select")
            if st.button("🗑️ Eliminar seleccionado", key="mb_delete_btn"):
                confirm_key = "_mb_confirm_delete"
                if st.session_state.get(confirm_key) != selected_label:
                    st.session_state[confirm_key] = selected_label
                    show_warning_message(f"Presiona nuevamente 'Eliminar' para confirmar la eliminación de ID {opts[selected_label]}")
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


def _render_export(filtered_df: pd.DataFrame, start_date, end_date, selected_person, selected_process):
    if not _EXCEL_AVAILABLE:
        st.caption("Exportación a Excel no disponible en este entorno.")
        return
    safe_start = _safe_date_str(start_date)
    safe_end = _safe_date_str(end_date)
    period_label = f"{safe_start} - {safe_end}" if (safe_start or safe_end) else "Período no especificado"
    try:
        report = build_processes_report_cached(
            df_current=filtered_df, df_previous=None,
            selected_person=selected_person if selected_person != ALL_OPTION else None,
            selected_process=selected_process if selected_process != ALL_OPTION else None,
        )
        excel_bytes = export_processes_report_cached(report, period_label=period_label)
        suffix = f"{selected_person}" if selected_person else ""
        filename = f"INFORME_PRODUCTIVIDAD_PROCESOSMANUALES_{suffix}.xlsx"
        create_excel_download_button(excel_bytes, filename=filename, label="📥 Descargar informe de productividad (Excel)")
    except Exception as e:
        show_error_message(f"Error generando informe: {e}")


def render_tab_manual_billing():
    st.header("Productividad de Procesos Administrativos")
    st.markdown("Registra, filtra y visualiza la productividad de los procesos administrativos.")

    service = ManualBillingFrontendService()

    _render_registration_form(service)

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
    if not records:
        st.info("No hay registros. Usa el formulario de registro para agregar datos.")
        return

    df = service.to_dataframe(records)

    start_date, end_date, selected_person, selected_process = _render_filters(df)

    filtered_df = service.filter_dataframe(
        df,
        start_date=start_date,
        end_date=end_date,
        person=selected_person if selected_person != ALL_OPTION else None,
        process=selected_process if selected_process != ALL_OPTION else None,
    )

    kpis = service.get_kpis_from_df(filtered_df)
    _render_kpis(kpis)

    chart_data = service.build_chart_datasets(
        filtered_df,
        selected_person=selected_person,
        selected_process=selected_process,
    )
    _render_charts(chart_data)

    _render_records_table(service, records, filtered_df)

    _render_export(filtered_df, start_date, end_date, selected_person, selected_process)
