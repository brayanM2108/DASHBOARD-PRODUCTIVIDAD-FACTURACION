"""
📋 Control de Radicación — Dashboard Ejecutivo
================================================
Monitoreo del cumplimiento del SLA de radicación de facturas.

Inspired by: Power BI, Grafana Enterprise, Metabase, Looker
Design System: GolemanTheme
"""

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from backend.app.etl.billers_processor import resolve_document_to_name
from backend.app.etl.loaders import load_billers_master_cached
from frontend.components.visualizations import (
    plot_rad_donut,
    plot_rad_distribucion_antiguedad,
    plot_rad_top_usuarios,
    plot_rad_vencidas_por_dia,
    clear_viz_filter,
    any_viz_filter_active,
)
from frontend.models.radicacion import RadicacionMetrics
from frontend.services.radicacion_service import RadicacionFrontendService
from ui.goleman_theme import GolemanTheme

ALL_OPTION = "Todos"
RADICACION_THRESHOLD = 2

COLOR_DENTRO = GolemanTheme.SUCCESS
COLOR_PROXIMO = GolemanTheme.ORANGE
COLOR_VENCIDO = GolemanTheme.DANGER


def _prepare_radicacion_df(df: pd.DataFrame) -> pd.DataFrame | None:
    """Replica la lógica del backend para obtener métricas por factura."""
    if df is None or df.empty:
        return None

    fact_col = next((c for c in ["FACTURA"] if c in df.columns), None)
    user_col = next((c for c in ["USUARIO"] if c in df.columns), None)
    fecha_col = next((c for c in ["FECHA FACTURA"] if c in df.columns), None)
    rad_panacea = next((c for c in ["RADICADO PANACEA"] if c in df.columns), None)
    rad_externo = next((c for c in ["RADICADO EXTERNO"] if c in df.columns), None)

    if not fact_col or not user_col or not fecha_col:
        return None

    result = df[[fact_col, user_col, fecha_col]].copy()
    result[fecha_col] = pd.to_datetime(result[fecha_col], errors="coerce")
    result = result.dropna(subset=[fecha_col])
    result = result.drop_duplicates(subset=[fact_col])
    result[user_col] = result[user_col].astype(str).str.strip()
    result = result[result[user_col].notna() & (result[user_col] != "")]

    result["RADICADO"] = False
    if rad_panacea and rad_panacea in df.columns:
        rad_p = pd.to_numeric(df[rad_panacea], errors="coerce").notna()
        result["RADICADO"] = result["RADICADO"] | rad_p.reindex(result.index, fill_value=False)
    if rad_externo and rad_externo in df.columns:
        rad_e = pd.to_numeric(df[rad_externo], errors="coerce").notna()
        result["RADICADO"] = result["RADICADO"] | rad_e.reindex(result.index, fill_value=False)

    today = pd.Timestamp.now().normalize()
    result["DIAS_SIN_RADICAR"] = (today - result[fecha_col]).dt.days
    result["VENCIDA"] = (~result["RADICADO"]) & (result["DIAS_SIN_RADICAR"] > RADICACION_THRESHOLD)
    result["FECHA_LIMITE"] = result[fecha_col] + pd.Timedelta(days=RADICACION_THRESHOLD)

    return result


def _classify_user(pct_vencidas: float) -> tuple[str, str]:
    if pct_vencidas <= 10:
        return "Excelente", "success"
    elif pct_vencidas <= 30:
        return "Riesgo", "warning"
    else:
        return "Crítico", "danger"


def _render_header():
    st.markdown(
        f"""
        <div style="margin-bottom:8px">
            <div style="font-size:22px;font-weight:700;color:{GolemanTheme.NAVY};display:flex;align-items:center;gap:10px">
                <span></span> Control de Radicación
            </div>
            <div style="font-size:13px;color:{GolemanTheme.MUTED};margin-top:4px">
                Monitoreo del cumplimiento del SLA de radicación de facturas
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_kpi_card(label: str, value: str, icon: str, color: str, sub: str = ""):
    return (
        f'<div style="background:{GolemanTheme.WHITE};border:0.5px solid {GolemanTheme.BORDER};'
        f'border-left:3px solid {color};border-radius:10px;padding:16px 18px;'
        f'box-shadow:0 1px 4px rgba(0,9,39,.04)">'
        f'<div style="font-size:10px;color:{GolemanTheme.MUTED};text-transform:uppercase;'
        f'letter-spacing:.05em;font-weight:500">{icon} {label}</div>'
        f'<div style="font-size:26px;font-weight:700;color:{GolemanTheme.NAVY};margin-top:6px">{value}</div>'
        f'{f"<div style=\"font-size:11px;color:{GolemanTheme.MUTED};margin-top:4px\">{sub}</div>" if sub else ""}'
        f'</div>'
    )


def _render_kpis(total: int, vencidas: int, dentro_sla: int, cumplimiento: float, prom_dias: float):
    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        st.markdown(_render_kpi_card("Total Facturas", f"{total:,}", "📄", GolemanTheme.BLUE), unsafe_allow_html=True)

    with k2:
        color_v = COLOR_VENCIDO if vencidas > 0 else GolemanTheme.MUTED
        st.markdown(_render_kpi_card("Facturas Vencidas", f"{vencidas:,}", "🔴", color_v), unsafe_allow_html=True)

    with k3:
        st.markdown(_render_kpi_card("Dentro del SLA", f"{dentro_sla:,}", "🟢", COLOR_DENTRO), unsafe_allow_html=True)

    with k4:
        color_c = COLOR_DENTRO
        st.markdown(
            _render_kpi_card("Cumplimiento SLA", f"{cumplimiento:.1f}%", "📊", color_c),
            unsafe_allow_html=True,
        )

    with k5:
        st.markdown(_render_kpi_card("Promedio días", f"{prom_dias:.1f}", "⏱", GolemanTheme.ORANGE), unsafe_allow_html=True)


def _render_alerts(vencidas: int, cumplimiento: float, usuarios_criticos: list, facturas_7dias: int):
    alertas = []
    if vencidas > 0:
        alertas.append(f"<b>{vencidas:,} facturas vencidas</b> requieren atención inmediata.")
    if usuarios_criticos:
        names = ", ".join(usuarios_criticos[:3])
        alertas.append(f"<b>{len(usuarios_criticos)} usuarios</b> concentran la mayor cantidad de vencidas: {names}.")
    if facturas_7dias > 0:
        alertas.append(f"<b>{facturas_7dias} facturas</b> tienen más de 7 días sin radicar.")

    if not alertas:
        alertas.append("No hay alertas operativas. El proceso está dentro del SLA.")

    items = "".join(f'<div style="padding:4px 0;font-size:12.5px;color:{GolemanTheme.TEXT}">• {a}</div>' for a in alertas)

    st.markdown(
        f'<div style="background:{GolemanTheme.ORANGE_LIGHT};border:0.5px solid {GolemanTheme.BORDER};'
        f'border-left:3px solid {GolemanTheme.ORANGE};border-radius:10px;padding:16px 20px;margin-bottom:20px">'
        f'<div style="font-size:11px;font-weight:600;color:{GolemanTheme.ORANGE};text-transform:uppercase;'
        f'letter-spacing:.06em;margin-bottom:8px">⚠ Alertas Operativas</div>'
        f'{items}'
        f'</div>',
        unsafe_allow_html=True,
    )


def _section_title(text: str):
    st.markdown(
        f'<div style="font-size:13px;font-weight:600;color:{GolemanTheme.NAVY};'
        f'border-left:3px solid {GolemanTheme.ORANGE};padding-left:10px;margin-bottom:12px">'
        f'{text}</div>',
        unsafe_allow_html=True,
    )


def _inject_chart_grid_css():
    st.markdown(
        f"""
        <style>
        #chart-grid-start ~ div[data-testid="stHorizontalBlock"] {{
            gap: 16px !important;
        }}
        #chart-grid-start ~ div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
            background: {GolemanTheme.WHITE};
            border: 0.5px solid {GolemanTheme.BORDER};
            border-left: 3px solid {GolemanTheme.ORANGE};
            border-radius: 10px; !important;
            padding: 16px;
            box-shadow: 0 1px 4px rgba(0,9,39,.04);
            transition: all 0.2s ease;
        }}
        #chart-grid-start ~ div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:hover {{
            box-shadow: 0 4px 12px rgba(0,9,39,.12);
            transform: translateY(-2px);
        }}
        #chart-grid-start ~ div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div {{
            height: 100%;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_user_table(df_by_user: pd.DataFrame):
    if df_by_user is None or df_by_user.empty:
        st.info("No hay datos por usuario.")
        return

    df = df_by_user.copy()
    df["RADICADAS"] = df["TOTAL"] - df["VENCIDAS"]
    df["% VENCIDAS"] = (df["VENCIDAS"] / df["TOTAL"] * 100).round(1)
    df = df.sort_values("VENCIDAS", ascending=False).reset_index(drop=True)

    def _badge(row):
        estado, kind = _classify_user(row["% VENCIDAS"])
        return f"{estado}"

    df["ESTADO"] = df.apply(_badge, axis=1)

    display_df = df[["USUARIO", "TOTAL", "RADICADAS", "VENCIDAS", "% VENCIDAS", "ESTADO"]]

    st.dataframe(
        display_df,
        column_config={
            "USUARIO": "Usuario",
            "TOTAL": st.column_config.NumberColumn("Total", format="%d"),
            "RADICADAS": st.column_config.NumberColumn("Radicadas", format="%d"),
            "VENCIDAS": st.column_config.NumberColumn("Vencidas", format="%d"),
            "% VENCIDAS": st.column_config.NumberColumn("% Vencidas", format="%.1f%%"),
            "ESTADO": "Estado",
        },
        use_container_width=True,
        hide_index=True,
    )


def _render_critical_invoices(df_radicacion: pd.DataFrame):
    if df_radicacion is None or df_radicacion.empty:
        st.info("No hay datos de facturas.")
        return

    criticas = df_radicacion[
        (df_radicacion["VENCIDA"] == True)
    ].copy()

    if criticas.empty:
        st.markdown(
            f'<div style="background:{GolemanTheme.SUCCESS_LIGHT};border:0.5px solid {GolemanTheme.BORDER};'
            f'border-left:3px solid {GolemanTheme.SUCCESS};border-radius:10px;padding:16px 20px;'
            f'margin-bottom:16px">'
            f'<div style="font-size:13px;color:{GolemanTheme.SUCCESS};font-weight:500">'
            f'No hay facturas cr\u00edticas. Todas las facturas est\u00e1n dentro del SLA.</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        return

    fact_col = next((c for c in ["FACTURA"] if c in criticas.columns), None)
    user_col = next((c for c in ["USUARIO"] if c in criticas.columns), None)
    fecha_col = next((c for c in ["FECHA FACTURA"] if c in criticas.columns), None)

    criticas = criticas.sort_values("DIAS_SIN_RADICAR", ascending=False)

    def _estado_label(dias):
        if dias > 7:
            return "Cr\u00edtico"
        elif dias > 4:
            return "Alto riesgo"
        return "Vencida"

    def _prioridad_label(dias):
        if dias > 7:
            return "Alta"
        elif dias > 4:
            return "Media"
        return "Baja"

    display_rows = []
    for _, row in criticas.iterrows():
        factura = str(row.get(fact_col, "")) if fact_col else ""
        usuario = str(row.get(user_col, "")) if user_col else ""
        fecha_fact = row[fecha_col].strftime("%Y-%m-%d") if fecha_col and pd.notna(row.get(fecha_col)) else ""
        fecha_lim = row["FECHA_LIMITE"].strftime("%Y-%m-%d") if pd.notna(row.get("FECHA_LIMITE")) else ""
        dias = int(row["DIAS_SIN_RADICAR"])
        display_rows.append({
            "Factura": factura,
            "Usuario": usuario,
            "Fecha Factura": fecha_fact,
            "Fecha L\u00edmite": fecha_lim,
            "D\u00edas": dias,
            "Estado": _estado_label(dias),
            "Prioridad": _prioridad_label(dias),
        })

    display_df = pd.DataFrame(display_rows)

    st.dataframe(
        display_df,
        column_config={
            "Factura": "Factura",
            "Usuario": "Usuario",
            "Fecha Factura": st.column_config.DateColumn("Fecha Factura", format="DD/MM/YYYY"),
            "Fecha L\u00edmite": st.column_config.DateColumn("Fecha L\u00edmite", format="DD/MM/YYYY"),
            "D\u00edas": st.column_config.NumberColumn("D\u00edas", format="%d"),
            "Estado": "Estado",
            "Prioridad": "Prioridad",
        },
        use_container_width=True,
        hide_index=True,
    )


def _render_insights(total: int, vencidas: int, cumplimiento: float, df_by_user: pd.DataFrame, df_radicacion: pd.DataFrame):
    insights = []

    if total > 0:
        pct_venc = (vencidas / total * 100) if total > 0 else 0
        insights.append(
            f"El <b>{pct_venc:.1f}%</b> de las facturas incumplen el SLA de radicación "
            f"({vencidas:,} de {total:,} facturas)."
        )

    if df_by_user is not None and not df_by_user.empty:
        top_user = df_by_user.loc[df_by_user["VENCIDAS"].idxmax()]
        if top_user["VENCIDAS"] > 0:
            pct_top = (top_user["VENCIDAS"] / vencidas * 100) if vencidas > 0 else 0
            insights.append(
                f"<b>{top_user['USUARIO']}</b> concentra el <b>{pct_top:.0f}%</b> "
                f"de las facturas vencidas ({int(top_user['VENCIDAS']):,} facturas)."
            )

    if df_radicacion is not None and not df_radicacion.empty:
        vencidas_df = df_radicacion[df_radicacion["VENCIDA"] == True]
        if not vencidas_df.empty:
            fecha_col = next((c for c in ["FECHA FACTURA"] if c in vencidas_df.columns), None)
            if fecha_col:
                today = pd.Timestamp.now().normalize()
                last_3 = today - pd.Timedelta(days=3)
                recent = vencidas_df[vencidas_df[fecha_col] >= last_3]
                if len(recent) > 0:
                    insights.append(
                        f"En los últimos 3 días se generaron <b>{len(recent):,} facturas vencidas</b> "
                        f"que requieren atención prioritaria."
                    )

    usuarios_riesgo = []
    if df_by_user is not None and not df_by_user.empty:
        for _, row in df_by_user.iterrows():
            pct = (row["VENCIDAS"] / row["TOTAL"] * 100) if row["TOTAL"] > 0 else 0
            if pct > 30 and row["VENCIDAS"] >= 5:
                usuarios_riesgo.append(row["USUARIO"])
    if usuarios_riesgo:
        insights.append(
            f"Se recomienda priorizar los usuarios con mayor porcentaje de vencidas: "
            f"<b>{', '.join(usuarios_riesgo[:3])}</b>."
        )

    items = "".join(
        f'<div style="padding:6px 0;font-size:12.5px;color:{GolemanTheme.TEXT};border-bottom:0.5px solid {GolemanTheme.BORDER}">'
        f'{i}</div>'
        for i in insights
    )

    st.markdown(
        f'<div style="background:{GolemanTheme.WHITE};border:0.5px solid {GolemanTheme.BORDER};'
        f'border-left:3px solid {GolemanTheme.BLUE};border-radius:10px;padding:16px 20px;margin-top:20px">'
        f'<div style="font-size:11px;font-weight:600;color:{GolemanTheme.BLUE};text-transform:uppercase;'
        f'letter-spacing:.06em;margin-bottom:8px">💡 Resumen Ejecutivo</div>'
        f'{items}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_tab_radicacion():
    _render_header()

    start_date = st.session_state.get("global_start_date")
    end_date = st.session_state.get("global_end_date")
    selected_user = st.session_state.get("global_user", ALL_OPTION)

    # Normalizar selected_user: puede ser string, lista, o None
    if isinstance(selected_user, list):
        if len(selected_user) == 0 or selected_user[0] == ALL_OPTION:
            selected_user = ALL_OPTION
        else:
            selected_user = selected_user[0] if len(selected_user) == 1 else ALL_OPTION

    user = st.session_state.get("user", {})
    role = user.get("role") if user else None
    if role in ("ADMIN", "SUPERVISOR"):
        selected_users = None if selected_user == ALL_OPTION else [selected_user]
    else:
        selected_users = None

    token = st.session_state.get("token")
    if not token:
        st.warning("Debes iniciar sesión para ver Radicación.")
        return

    service = RadicacionFrontendService(token=token)
    result = service.get_metrics(
        start_date=start_date,
        end_date=end_date,
        selected_users=selected_users,
    )

    if result.error:
        st.error(result.error)
        return

    total = result.total
    vencidas = result.vencidas
    dentro_sla = total - vencidas
    cumplimiento = ((dentro_sla / total * 100) if total > 0 else 0.0)

    df_by_user = pd.DataFrame([r.__dict__ for r in result.by_user]) if result.by_user else pd.DataFrame()

    # Preparar DataFrame de radicación desde session_state
    df_radicacion = _prepare_radicacion_df(st.session_state.get("electronic_billing_df"))

    # Inicializar métricas
    prom_dias = 0.0
    facturas_7dias = 0
    proximas_a_vencer = 0

    if df_radicacion is None or df_radicacion.empty:
        st.warning("No hay datos de facturación electrónica disponibles. Las gráficas no se mostrarán.")
        df_radicacion = None
    else:
        # Filtrar por rol de usuario
        if role not in ("ADMIN", "SUPERVISOR"):
            user_doc = user.get("document")
            if user_doc:
                billers_df = load_billers_master_cached()
                biller_name = resolve_document_to_name(billers_df, user_doc)
                if biller_name and biller_name != str(user_doc):
                    user_col = next((c for c in ["USUARIO"] if c in df_radicacion.columns), None)
                    if user_col:
                        df_radicacion = df_radicacion[
                            df_radicacion[user_col].astype(str).str.strip().str.upper()
                            == biller_name.strip().upper()
                        ]

        # Filtrar por fechas
        fecha_col = next((c for c in ["FECHA FACTURA"] if c in df_radicacion.columns), None)
        if fecha_col:
            if start_date:
                df_radicacion = df_radicacion[df_radicacion[fecha_col].dt.date >= start_date]
            if end_date:
                df_radicacion = df_radicacion[df_radicacion[fecha_col].dt.date <= end_date]

        # Filtrar por usuario seleccionado
        user_col = next((c for c in ["USUARIO"] if c in df_radicacion.columns), None)
        if user_col and selected_users:
            selected_set = {str(u).strip().upper() for u in selected_users}
            df_radicacion = df_radicacion[
                df_radicacion[user_col].astype(str).str.strip().str.upper().isin(selected_set)
            ]

        # Calcular métricas adicionales
        pendientes = df_radicacion[df_radicacion["RADICADO"] == False]
        prom_dias = float(pendientes["DIAS_SIN_RADICAR"].mean()) if not pendientes.empty else 0.0
        facturas_7dias = int((pendientes["DIAS_SIN_RADICAR"] > 7).sum())
        proximas_a_vencer = int(((pendientes["DIAS_SIN_RADICAR"] >= 1) & (pendientes["DIAS_SIN_RADICAR"] <= RADICACION_THRESHOLD)).sum())

    # Identificar usuarios críticos
    usuarios_criticos = []
    if not df_by_user.empty:
        for _, row in df_by_user.iterrows():
            pct = (row["VENCIDAS"] / row["TOTAL"] * 100) if row["TOTAL"] > 0 else 0
            if pct > 30 and row["VENCIDAS"] >= 5:
                usuarios_criticos.append(row["USUARIO"])

    # Renderizar KPIs
    st.markdown('<div style="margin-bottom:20px">', unsafe_allow_html=True)
    _render_kpis(total, vencidas, dentro_sla, cumplimiento, prom_dias)
    st.markdown('</div>', unsafe_allow_html=True)

    # Renderizar alertas
    _render_alerts(vencidas, cumplimiento, usuarios_criticos, facturas_7dias)

    # Renderizar gráficas (solo si hay datos)
    _inject_chart_grid_css()
    st.markdown('<div id="chart-grid-start"></div>', unsafe_allow_html=True)

    _VIZ_KEY = "radicacion"

    if any_viz_filter_active(_VIZ_KEY):
        if st.button("Limpiar filtro", key="clear_rad_filter", use_container_width=True):
            clear_viz_filter(_VIZ_KEY)
            st.rerun()

    col1, col2, col3, col4 = st.columns(4, gap="small")
    with col1:
        _section_title("Estado de facturas")
        plot_rad_donut(dentro_sla, proximas_a_vencer, vencidas, view_key=_VIZ_KEY)

    with col2:
        _section_title("Facturas vencidas por día")
        if df_radicacion is not None and not df_radicacion.empty:
            plot_rad_vencidas_por_dia(df_radicacion, view_key=_VIZ_KEY)
        else:
            st.info("Sin datos para mostrar")

    with col3:
        _section_title("Top usuarios con facturas vencidas")
        if not df_by_user.empty:
            plot_rad_top_usuarios(df_by_user, view_key=_VIZ_KEY)
        else:
            st.info("Sin datos de usuarios")

    with col4:
        _section_title("Distribución por antigüedad")
        if df_radicacion is not None and not df_radicacion.empty:
            plot_rad_distribucion_antiguedad(df_radicacion, view_key=_VIZ_KEY)
        else:
            st.info("Sin datos para mostrar")

    # Renderizar tablas
    col_tab1, col_tab2 = st.columns(2, gap="medium")
    with col_tab1:
        _section_title("Resumen por usuario")
        _render_user_table(df_by_user)

    with col_tab2:
        _section_title("Facturas criticas (vencidas ordenadas por antiguedad)")
        _render_critical_invoices(df_radicacion)

    # ── Export section ──
    from frontend.components.export_panel import render_export_section
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    render_export_section("radicacion", allow_user_filter=True)

    # Renderizar insights
    _render_insights(total, vencidas, cumplimiento, df_by_user, df_radicacion)
