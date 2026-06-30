"""
Home Page — Executive & Personal Dashboard
============================================
- Admin / Supervisor: dashboard ejecutivo global
- Facturador / Analista: panel de productividad personal

Design system: GolemanTheme (palette, helpers, CSS classes).
No inline <style> blocks — only style="" with palette values.
"""

from datetime import datetime, date, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from frontend.models.home import (
    HomeAdminResponse,
    HomeUserResponse,
    HomeAdminTrendPoint,
    HomeUserTrendPoint,
)
from frontend.services.home_service import HomeFrontendService
from ui.goleman_theme import GolemanTheme


class HomePage:

    @classmethod
    def render(cls):
        user = st.session_state.get("user", {})
        role = user.get("role", "")
        token = st.session_state.get("token")

        start_date = st.session_state.get("global_start_date", date.today() - timedelta(days=29))
        end_date = st.session_state.get("global_end_date", date.today())

        service = HomeFrontendService(token=token)

        try:
            if role in ("ADMIN", "SUPERVISOR"):
                filter_user = st.session_state.get("global_user")
                if filter_user in ("Todos", ["Todos"], None):
                    filter_user = None
                elif isinstance(filter_user, list) and len(filter_user) == 1:
                    filter_user = filter_user[0]

                data = service.get_admin_summary(start_date, end_date, filter_user)
                cls._render_admin_dashboard(data, user)
            else:
                data = service.get_user_summary(start_date, end_date)
                cls._render_user_dashboard(data, user)
        except Exception as e:
            st.error(f"Error cargando dashboard: {e}")

    # ══════════════════════════════════════════════
    #  ADMIN / SUPERVISOR DASHBOARD
    # ══════════════════════════════════════════════

    @classmethod
    def _render_admin_dashboard(cls, data: HomeAdminResponse, user: dict):
        nombre = user.get("username", "")
        rol = user.get("role", "")
        hoy = datetime.now()

        cls._render_hero_admin(nombre, rol, hoy, data)
        cls._render_kpis_admin(data)
        cls._render_charts_row_admin(data)
        cls._render_top_users_admin(data)
        cls._render_alerts_insights_row_admin(data)


    @classmethod
    def _render_hero_admin(cls, nombre: str, rol: str, hoy: datetime, data: HomeAdminResponse):
        leg_count = data.modules.legalizaciones
        valor = data.kpis.total_valor_tercero
        horas_eq = data.kpis.horas_productivas_equipo

        def _fmt_money(v):
            if abs(v) >= 1_000_000_000:
                return f"${v / 1_000_000_000:,.1f}B"
            elif abs(v) >= 1_000_000:
                return f"${v / 1_000_000:,.1f}M"
            return f"${v:,.0f}"

        st.markdown(f"""
        <div style="
            background:{GolemanTheme.NAVY};
            border-radius:14px;
            padding:20px 28px;
            display:flex;
            align-items:center;
            justify-content:space-between;
            position:relative;
            overflow:hidden;
            margin-bottom:18px;
        ">
          <div style="position:relative;z-index:1">
            <div style="font-size:11px;color:rgba(255,255,255,.4);
                        letter-spacing:.06em;text-transform:uppercase;
                        margin-bottom:5px">Dashboard ejecutivo</div>
            <div style="font-size:20px;font-weight:600;color:#fff;margin-bottom:3px">
              Bienvenido/a, {nombre}
            </div>
            <div style="font-size:12px;color:rgba(255,255,255,.4)">
              {rol} · Goleman IPS
            </div>
            <div style="font-size:11px;color:rgba(255,255,255,.28);
                        margin-top:8px;display:flex;align-items:center;gap:5px">
              📅 {hoy.strftime("%A %d de %B de %Y").capitalize()}
            </div>
          </div>
          <div style="display:flex;gap:14px;position:relative;z-index:1">
            {cls._hero_stat("Legalizaciones", f"{leg_count:,}")}
            {cls._hero_stat("Valor Facturado", _fmt_money(valor), accent=True)}
            {cls._hero_stat("Horas productivas", f"{horas_eq:.0f}h", accent=False)}
          </div>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def _hero_stat(label: str, value: str, accent: bool = False) -> str:
        bg = "rgba(249,120,56,.1)" if accent else "rgba(255,255,255,.07)"
        border = "rgba(249,120,56,.3)" if accent else "rgba(255,255,255,.1)"
        color = "#F97838" if accent else "#fff"
        return f"""
        <div style="background:{bg};border:0.5px solid {border};border-radius:10px;
                    padding:10px 16px;text-align:center;min-width:85px">
          <div style="font-size:18px;font-weight:600;color:{color}">{value}</div>
          <div style="font-size:10px;color:rgba(255,255,255,.4);margin-top:2px;white-space:nowrap">{label}</div>
        </div>"""

    @classmethod
    def _render_kpis_admin(cls, data: HomeAdminResponse):
        def _fmt_money(v):
            if abs(v) >= 1_000_000_000:
                return f"${v / 1_000_000_000:,.1f}B"
            elif abs(v) >= 1_000_000:
                return f"${v / 1_000_000:,.1f}M"
            return f"${v:,.0f}"

        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            st.metric("Total registros", f"{data.kpis.total_records:,}")
        with k2:
            st.metric("Registros hoy", f"{data.kpis.records_today:,}")
        with k3:
            st.metric("Usuarios activos", str(data.kpis.active_users))
        with k4:
            st.metric("Valor facturado", _fmt_money(data.kpis.total_valor_tercero))
        with k5:
            st.metric("Productividad", f"{data.kpis.cumplimiento_horas:.0f}%")

    @classmethod
    def _render_charts_row_admin(cls, data: HomeAdminResponse):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(GolemanTheme.section_header("Evolución general", "Registros procesados últimos 7 días"), unsafe_allow_html=True)
            cls._render_trend_chart_admin(data.trend)
        with col2:
            st.markdown(GolemanTheme.section_header("Distribución", "Participación por módulo"), unsafe_allow_html=True)
            cls._render_donut_admin(data.modules)

    @classmethod
    def _render_trend_chart_admin(cls, trend: list[HomeAdminTrendPoint]):
        if not trend:
            st.markdown(f'<div class="g-chart-card"><div class="g-muted-note">No hay datos de tendencia.</div></div>', unsafe_allow_html=True)
            return

        rows = []
        for point in trend:
            fecha_fmt = datetime.strptime(point.fecha, "%Y-%m-%d").strftime("%a %d/%m")
            rows.append({"Fecha": fecha_fmt, "Registros": point.legalizaciones, "Módulo": "Legalizaciones"})
            rows.append({"Fecha": fecha_fmt, "Registros": point.facturacion, "Módulo": "Facturación"})
            rows.append({"Fecha": fecha_fmt, "Registros": point.rips, "Módulo": "RIPS"})
            rows.append({"Fecha": fecha_fmt, "Registros": point.procesos, "Módulo": "Procesos"})

        df_trend = pd.DataFrame(rows)

        color_map = {
            "Legalizaciones": GolemanTheme.BLUE,
            "Facturación": GolemanTheme.ORANGE,
            "RIPS": GolemanTheme.SUCCESS,
            "Procesos": GolemanTheme.NAVY2,
        }

        fig = px.line(
            df_trend, x="Fecha", y="Registros", color="Módulo",
            color_discrete_map=color_map, markers=True,
        )
        fig.update_traces(
            line=dict(width=2), marker=dict(size=5),
            hovertemplate="%{x}<br>%{legendgroup}: %{y:,.0f}<extra></extra>",
        )
        fig.update_layout(
            height=280, margin=dict(l=10, r=10, t=8, b=10),
            font=dict(color=GolemanTheme.TEXT, size=11),
            paper_bgcolor="white", plot_bgcolor="white",
            legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center", font=dict(size=10)),
            yaxis=dict(gridcolor="#EDF1F7", zerolinecolor="#EDF1F7"),
            xaxis=dict(gridcolor="#EDF1F7"), hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

    @classmethod
    def _render_donut_admin(cls, modules):
        module_counts = {
            "Legalizaciones": modules.legalizaciones,
            "Facturación": modules.facturacion,
            "RIPS": modules.rips,
            "Radicación": modules.radicacion,
            "Procesos": modules.procesos,
        }
        total = sum(module_counts.values())
        if total == 0:
            st.markdown(f'<div class="g-chart-card"><div class="g-muted-note">No hay datos para distribución.</div></div>', unsafe_allow_html=True)
            return

        colors = [GolemanTheme.BLUE, GolemanTheme.ORANGE, GolemanTheme.SUCCESS, GolemanTheme.DANGER, GolemanTheme.NAVY2]
        labels = list(module_counts.keys())
        values = list(module_counts.values())

        fig = go.Figure(data=[go.Pie(
            labels=labels, values=values, hole=0.55,
            marker=dict(colors=colors[:len(labels)]),
            textinfo="label+percent",
            textfont=dict(size=11, color=GolemanTheme.TEXT),
            hovertemplate="%{label}<br>%{value:,} registros (%{percent})<extra></extra>",
        )])
        fig.update_layout(
            height=280, margin=dict(l=10, r=10, t=8, b=10),
            showlegend=False, font=dict(color=GolemanTheme.TEXT),
            paper_bgcolor="white", plot_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True)

    @classmethod
    def _render_top_users_admin(cls, data: HomeAdminResponse):
        st.markdown(GolemanTheme.section_header("Top usuarios"), unsafe_allow_html=True)
        cls._render_ranking_admin(data.top_users)

    @classmethod
    def _render_ranking_admin(cls, top_users):
        if not top_users or top_users[0].registros == 0:
            st.markdown(f'<div class="g-chart-card"><div class="g-muted-note">No hay datos de usuarios.</div></div>', unsafe_allow_html=True)
            return

        colors = [GolemanTheme.BLUE, GolemanTheme.NAVY2, GolemanTheme.ORANGE, GolemanTheme.SUCCESS, GolemanTheme.MUTED]
        fig = go.Figure()
        for i, user in enumerate(top_users):
            horas = getattr(user, "horas_productivas", 0.0)
            fig.add_trace(go.Bar(
                y=[user.usuario], x=[user.registros],
                orientation="h", marker=dict(color=colors[i % len(colors)], cornerradius=4),
                text=[f"{user.registros:,} reg"], textposition="outside",
                hovertemplate=f"%{{y}}<br>%{{x:,}} registros<br>{horas:.1f}h productivas<extra></extra>",
                showlegend=False,
            ))
        fig.update_layout(
            height=max(200, len(top_users) * 45 + 40),
            margin=dict(l=10, r=50, t=8, b=10),
            font=dict(color=GolemanTheme.TEXT, size=11),
            paper_bgcolor="white", plot_bgcolor="white",
            xaxis=dict(visible=False, zeroline=False),
            yaxis=dict(autorange="reversed", gridcolor="#EDF1F7", zeroline=False),
            barmode="stack",
        )
        st.plotly_chart(fig, use_container_width=True)

    @classmethod
    def _render_alerts_insights_row_admin(cls, data: HomeAdminResponse):
        col1, col2 = st.columns(2)
        with col1:
            cls._render_module_status_admin(data.modules)
        with col2:
            cls._render_alerts_admin(data.alerts)
        cls._render_insights_admin(data.insights)

    @classmethod
    def _render_module_status_admin(cls, modules):
        st.markdown(GolemanTheme.section_header("Estado de modulos"), unsafe_allow_html=True)
        module_list = [
            ("📋 Legalizaciones", modules.legalizaciones),
            ("💰 Facturacion", modules.facturacion),
            ("📄 RIPS", modules.rips),
            ("📋 Radicacion", modules.radicacion),
            ("⚙️ Procesos", modules.procesos),
        ]
        items = ""
        for label, count in module_list:
            status_color = GolemanTheme.SUCCESS if count > 0 else GolemanTheme.MUTED
            status_text = f"{count:,}" if count > 0 else "Sin datos"
            items += (
                f'<div style="display:flex;align-items:center;justify-content:space-between;'
                f'padding:8px 0;border-bottom:0.5px solid {GolemanTheme.BORDER}">'
                f'<span style="font-size:12px;color:{GolemanTheme.TEXT}">{label}</span>'
                f'<span style="font-size:12px;font-weight:600;color:{status_color}">{status_text}</span>'
                f'</div>'
            )
        st.markdown(f"""
        <div style="background:{GolemanTheme.WHITE};border:0.5px solid {GolemanTheme.BORDER};
                    border-left:3px solid {GolemanTheme.BLUE};border-radius:10px;
                    padding:12px 16px;box-shadow:0 1px 4px rgba(0,9,39,.04)">
          {items}
        </div>""", unsafe_allow_html=True)

    @classmethod
    def _render_alerts_admin(cls, alerts):
        st.markdown(GolemanTheme.section_header("Alertas criticas"), unsafe_allow_html=True)
        if not alerts:
            st.markdown(f"""
            <div style="background:{GolemanTheme.WHITE};border:0.5px solid {GolemanTheme.BORDER};
                        border-left:3px solid {GolemanTheme.SUCCESS};border-radius:10px;
                        padding:14px 16px;box-shadow:0 1px 4px rgba(0,9,39,.04)">
              <div style="font-size:12px;color:{GolemanTheme.MUTED}">Sin alertas criticas</div>
            </div>""", unsafe_allow_html=True)
            return

        alerts_html = "".join(
            f'<div style="display:flex;align-items:flex-start;gap:9px;padding:9px 11px;'
            f'border-radius:8px;background:{GolemanTheme.BG};margin-bottom:6px;font-size:12px;'
            f'color:{GolemanTheme.TEXT}">'
            f'<span style="flex-shrink:0;font-size:14px">{a.icon}</span>'
            f'<span>{a.text}</span></div>'
            for a in alerts
        )
        st.markdown(f"""
        <div style="background:{GolemanTheme.WHITE};border:0.5px solid {GolemanTheme.BORDER};
                    border-left:3px solid {GolemanTheme.DANGER};border-radius:10px;
                    padding:14px 16px 8px 16px;box-shadow:0 1px 4px rgba(0,9,39,.04)">
          {alerts_html}
        </div>""", unsafe_allow_html=True)

    @classmethod
    def _render_insights_admin(cls, insights):
        st.markdown(GolemanTheme.section_header("Insights"), unsafe_allow_html=True)
        if not insights:
            return
        items = "".join(
            f'<div style="display:flex;align-items:flex-start;gap:9px;padding:9px 11px;'
            f'border-radius:8px;background:{GolemanTheme.BG};margin-bottom:6px;font-size:12px">'
            f'<div style="width:7px;height:7px;border-radius:50%;background:{GolemanTheme.ORANGE};'
            f'flex-shrink:0;margin-top:4px"></div>'
            f'<div style="flex:1;line-height:1.4;color:{GolemanTheme.TEXT}">{i.text}</div></div>'
            for i in insights[:5]
        )
        st.markdown(f"""
        <div style="background:{GolemanTheme.WHITE};border:0.5px solid {GolemanTheme.BORDER};
                    border-left:3px solid {GolemanTheme.ORANGE};border-radius:10px;
                    padding:12px 16px 6px 16px;box-shadow:0 1px 4px rgba(0,9,39,.04)">
          {items}
        </div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════
    #  USER / FACTURADOR DASHBOARD
    # ══════════════════════════════════════════════

    @classmethod
    def _render_user_dashboard(cls, data: HomeUserResponse, user: dict):
        username = user.get("username", "Usuario")
        role = user.get("role", "")
        hoy = datetime.now()

        cls._render_hero_user(username, role, hoy, data)
        cls._render_kpis_user(data)
        cls._render_charts_row_user(data)
        cls._render_pendientes_alerts_user(data)
        cls._render_insights_user(data)

    @classmethod
    def _render_hero_user(cls, username: str, role: str, hoy: datetime, data: HomeUserResponse):
        horas = data.kpis.horas_productivas
        esperadas = data.kpis.horas_esperadas
        pct_bar = min(data.kpis.cumplimiento_horas, 100) if esperadas > 0 else 0

        horas_stat_html = f"""
        <div style="background:rgba(249,120,56,.1);border:0.5px solid rgba(249,120,56,.3);border-radius:10px;
                    padding:10px 14px;text-align:center;min-width:130px">
          <div style="font-size:18px;font-weight:600;color:#F97838">{horas:.1f}h</div>
          <div style="font-size:10px;color:rgba(255,255,255,.4);margin-top:2px;white-space:nowrap">de {esperadas:.0f}h</div>
          <div style="margin-top:6px;height:4px;background:rgba(255,255,255,.15);border-radius:3px;overflow:hidden">
            <div style="height:100%;width:{pct_bar:.0f}%;background:#F97838;border-radius:3px"></div>
          </div>
        </div>"""

        st.markdown(f"""
        <div style="
            background:{GolemanTheme.NAVY};
            border-radius:14px;
            padding:20px 28px;
            display:flex;
            align-items:center;
            justify-content:space-between;
            position:relative;
            overflow:hidden;
            margin-bottom:18px;
        ">
          <div style="position:relative;z-index:1">
            <div style="font-size:11px;color:rgba(255,255,255,.4);
                        letter-spacing:.06em;text-transform:uppercase;
                        margin-bottom:5px">Mi productividad</div>
            <div style="font-size:20px;font-weight:600;color:#fff;margin-bottom:3px">
              Hola, {username}
            </div>
            <div style="font-size:12px;color:rgba(255,255,255,.4);margin-bottom:8px">
              {role} · Goleman IPS
            </div>
            <div style="font-size:11px;color:rgba(255,255,255,.28)">
              {hoy.strftime('%A %d de %B de %Y').capitalize()}
            </div>
          </div>
          <div style="display:flex;gap:12px;position:relative;z-index:1;align-items:center">
            {cls._hero_stat("Registros hoy", f"{data.kpis.registros_hoy:,}")}
            {cls._hero_stat("Radic. pendientes", f"{data.kpis.radicaciones_pendientes:,}")}
            {horas_stat_html}
          </div>
        </div>
        """, unsafe_allow_html=True)

    @classmethod
    def _render_kpis_user(cls, data: HomeUserResponse):
        def _fmt_money(v):
            if abs(v) >= 1_000_000_000:
                return f"${v / 1_000_000_000:,.1f}B"
            elif abs(v) >= 1_000_000:
                return f"${v / 1_000_000:,.1f}M"
            return f"${v:,.0f}"

        k1, k2, k3, k4, k5, k6 = st.columns(6)
        with k1:
            st.metric("Legalizaciones", f"{data.modules.legalizaciones:,}")
        with k2:
            st.metric("Facturacion", f"{data.modules.facturacion:,}")
        with k3:
            st.metric("RIPS", f"{data.modules.rips:,}")
        with k4:
            st.metric("Radicacion", f"{data.modules.radicacion:,}")
        with k5:
            st.metric("Procesos", f"{data.modules.procesos:,}")
        with k6:
            st.metric("Productividad", f"{data.kpis.cumplimiento_horas:.0f}%")

    @classmethod
    def _render_charts_row_user(cls, data: HomeUserResponse):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(GolemanTheme.section_header("Mi avance semanal", "Registros procesados ultimos 7 dias"), unsafe_allow_html=True)
            cls._render_trend_chart_user(data.trend)
        with col2:
            st.markdown(GolemanTheme.section_header("Distribucion por modulo", "Participacion por modulo"), unsafe_allow_html=True)
            cls._render_donut_user(data.modules)

    @classmethod
    def _render_trend_chart_user(cls, trend: list[HomeUserTrendPoint]):
        if not trend or sum(t.registros for t in trend) == 0:
            st.markdown(f'<div class="g-chart-card"><div class="g-muted-note">Aun no hay registros esta semana.</div></div>', unsafe_allow_html=True)
            return

        rows = []
        for point in trend:
            fecha_fmt = datetime.strptime(point.fecha, "%Y-%m-%d").strftime("%a %d/%m")
            rows.append({"Fecha": fecha_fmt, "Registros": point.registros})

        df_trend = pd.DataFrame(rows)

        fig = px.area(
            df_trend, x="Fecha", y="Registros",
            markers=True,
            color_discrete_sequence=[GolemanTheme.BLUE],
        )
        fig.update_traces(
            line=dict(width=2, color=GolemanTheme.BLUE),
            fillcolor="rgba(21,101,192,.08)",
            marker=dict(size=6, color=GolemanTheme.BLUE),
            hovertemplate="%{x}: %{y:,.0f} registros<extra></extra>",
        )
        fig.update_layout(
            height=250, margin=dict(l=10, r=10, t=8, b=10),
            font=dict(color=GolemanTheme.TEXT, size=11),
            paper_bgcolor="white", plot_bgcolor="white",
            yaxis=dict(gridcolor="#EDF1F7", zerolinecolor="#EDF1F7"),
            xaxis=dict(gridcolor="#EDF1F7"),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    @classmethod
    def _render_donut_user(cls, modules):
        module_counts = {
            "Legalizaciones": modules.legalizaciones,
            "Facturacion": modules.facturacion,
            "RIPS": modules.rips,
            "Radicacion": modules.radicacion,
            "Procesos": modules.procesos,
        }
        total = sum(module_counts.values())
        if total == 0:
            st.markdown(f'<div class="g-chart-card"><div class="g-muted-note">No hay datos para mostrar.</div></div>', unsafe_allow_html=True)
            return

        colors = [GolemanTheme.BLUE, GolemanTheme.ORANGE, GolemanTheme.SUCCESS, GolemanTheme.DANGER, GolemanTheme.NAVY2]
        labels = list(module_counts.keys())
        values = list(module_counts.values())

        fig = go.Figure(data=[go.Pie(
            labels=labels, values=values, hole=0.55,
            marker=dict(colors=colors[:len(labels)]),
            textinfo="label+percent",
            textfont=dict(size=11, color=GolemanTheme.TEXT),
            hovertemplate="%{label}<br>%{value:,} registros (%{percent})<extra></extra>",
        )])
        fig.update_layout(
            height=280, margin=dict(l=10, r=10, t=8, b=10),
            showlegend=False, font=dict(color=GolemanTheme.TEXT),
            paper_bgcolor="white", plot_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True)

    @classmethod
    def _render_pendientes_alerts_user(cls, data: HomeUserResponse):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(GolemanTheme.section_header("Pendientes"), unsafe_allow_html=True)
            cls._render_pendientes_user(data.pendientes)
        with col2:
            st.markdown(GolemanTheme.section_header("Alertas"), unsafe_allow_html=True)
            cls._render_alerts_user(data.alerts)

    @classmethod
    def _render_pendientes_user(cls, pendientes):
        html = "".join(
            f'<div style="display:flex;align-items:center;gap:9px;padding:9px 11px;'
            f'border-radius:8px;background:{GolemanTheme.BG};margin-bottom:6px;font-size:12px">'
            f'<span style="flex-shrink:0;font-size:14px">{p.icon}</span>'
            f'<span style="color:{GolemanTheme.NAVY}">{p.text}</span></div>'
            for p in pendientes
        )
        st.markdown(f"""
        <div style="background:{GolemanTheme.WHITE};border:0.5px solid {GolemanTheme.BORDER};
                    border-left:3px solid {GolemanTheme.ORANGE};border-radius:10px;
                    padding:14px 16px;box-shadow:0 1px 4px rgba(0,9,39,.04)">
          {html}
        </div>""", unsafe_allow_html=True)

    @classmethod
    def _render_alerts_user(cls, alerts):
        html = "".join(
            f'<div style="display:flex;align-items:center;gap:9px;padding:9px 11px;'
            f'border-radius:8px;background:{GolemanTheme.BG};margin-bottom:6px;font-size:12px;'
            f'color:{GolemanTheme.NAVY}">{a.icon} {a.text}</div>'
            for a in alerts
        )
        st.markdown(f"""
        <div style="background:{GolemanTheme.WHITE};border:0.5px solid {GolemanTheme.BORDER};
                    border-left:3px solid {GolemanTheme.DANGER};border-radius:10px;
                    padding:14px 16px 8px 16px;box-shadow:0 1px 4px rgba(0,9,39,.04)">
          {html}
        </div>""", unsafe_allow_html=True)

    @classmethod
    def _render_insights_user(cls, data: HomeUserResponse):
        st.markdown(GolemanTheme.section_header("Insights"), unsafe_allow_html=True)
        if not data.insights:
            return
        items = "".join(
            f'<div style="display:flex;align-items:flex-start;gap:9px;padding:9px 11px;'
            f'border-radius:8px;background:{GolemanTheme.BG};margin-bottom:6px;font-size:12px">'
            f'<div style="width:7px;height:7px;border-radius:50%;background:{GolemanTheme.ORANGE};'
            f'flex-shrink:0;margin-top:4px"></div>'
            f'<div style="flex:1;line-height:1.4;color:{GolemanTheme.TEXT}">{i.text}</div></div>'
            for i in data.insights[:3]
        )
        st.markdown(f"""
        <div style="background:{GolemanTheme.WHITE};border:0.5px solid {GolemanTheme.BORDER};
                    border-left:3px solid {GolemanTheme.ORANGE};border-radius:10px;
                    padding:12px 16px 6px 16px;box-shadow:0 1px 4px rgba(0,9,39,.04)">
          {items}
        </div>""", unsafe_allow_html=True)
