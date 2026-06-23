import pandas as pd
import plotly.express as px
import streamlit as st

from frontend.services.legalizations_service import LegalizationsService
from ui.goleman_theme import GolemanTheme

ALL_OPTION = "Todos"


def _format_horas(horas: float) -> str:
    h = int(horas)
    m = int(round((horas - h) * 60))
    return f"{h}h {m:02d}m"


def render_tab_legalizations():
    st.markdown(
        GolemanTheme.section_header(
            "Legalizaciones",
            "PPL y Convenios",
        ),
        unsafe_allow_html=True,
    )

    start_date = st.session_state.get("global_start_date")
    end_date = st.session_state.get("global_end_date")
    selected_user = st.session_state.get("global_user", ALL_OPTION)

    user = st.session_state.get("user", {})
    role = user.get("role") if user else None
    if role in ("ADMIN", "SUPERVISOR"):
        selected_users = None if selected_user == ALL_OPTION else [selected_user]
    else:
        selected_users = None

    token = st.session_state.get("token")
    if not token:
        st.warning("Debes iniciar sesi\u00f3n para ver las legalizaciones.")
        return

    service = LegalizationsService()
    metrics = service.get_metrics(
        start_date=start_date,
        end_date=end_date,
        selected_users=selected_users,
    )

    if metrics.error:
        st.error(metrics.error)
        return

    tab_ppl, tab_agreements = st.tabs(["PPL", "Convenios"])

    with tab_ppl:
        _render_productivity_section(metrics=metrics.ppl, title="Legalizaciones PPL")

    with tab_agreements:
        _render_productivity_section(metrics=metrics.agreements, title="Legalizaciones Convenios")

    # ── Export section (una sola vez, fuera de los tabs internos) ──
    from frontend.components.export_panel import render_export_section
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    render_export_section("legalizations", allow_user_filter=True)


def _render_productivity_section(metrics, title: str):
    st.markdown(
        GolemanTheme.section_header(title),
        unsafe_allow_html=True,
    )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f'<div style="background:{GolemanTheme.WHITE};border:0.5px solid {GolemanTheme.BORDER};'
            f'border-left:3px solid {GolemanTheme.BLUE};border-radius:10px;padding:16px 18px;'
            f'box-shadow:0 1px 4px rgba(0,9,39,.04)">'
            f'<div style="font-size:10px;color:{GolemanTheme.MUTED};text-transform:uppercase;'
            f'letter-spacing:.05em;font-weight:500">Total registros</div>'
            f'<div style="font-size:26px;font-weight:700;color:{GolemanTheme.NAVY};margin-top:6px">{metrics.total:,}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f'<div style="background:{GolemanTheme.WHITE};border:0.5px solid {GolemanTheme.BORDER};'
            f'border-left:3px solid {GolemanTheme.ORANGE};border-radius:10px;padding:16px 18px;'
            f'box-shadow:0 1px 4px rgba(0,9,39,.04)">'
            f'<div style="font-size:10px;color:{GolemanTheme.MUTED};text-transform:uppercase;'
            f'letter-spacing:.05em;font-weight:500">Promedio diario</div>'
            f'<div style="font-size:26px;font-weight:700;color:{GolemanTheme.NAVY};margin-top:6px">{round(metrics.daily_average, 2):,}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            f'<div style="background:{GolemanTheme.WHITE};border:0.5px solid {GolemanTheme.BORDER};'
            f'border-left:3px solid {GolemanTheme.SUCCESS};border-radius:10px;padding:16px 18px;'
            f'box-shadow:0 1px 4px rgba(0,9,39,.04)">'
            f'<div style="font-size:10px;color:{GolemanTheme.MUTED};text-transform:uppercase;'
            f'letter-spacing:.05em;font-weight:500">Tiempo total</div>'
            f'<div style="font-size:26px;font-weight:700;color:{GolemanTheme.NAVY};margin-top:6px">{_format_horas(metrics.tiempo_total_horas)}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            f'<div style="background:{GolemanTheme.WHITE};border:0.5px solid {GolemanTheme.BORDER};'
            f'border-left:3px solid {GolemanTheme.ORANGE};border-radius:10px;padding:16px 18px;'
            f'box-shadow:0 1px 4px rgba(0,9,39,.04)">'
            f'<div style="font-size:10px;color:{GolemanTheme.MUTED};text-transform:uppercase;'
            f'letter-spacing:.05em;font-weight:500">Tiempo / día</div>'
            f'<div style="font-size:26px;font-weight:700;color:{GolemanTheme.NAVY};margin-top:6px">{_format_horas(metrics.tiempo_promedio_diario_horas)}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    tab_users, tab_dates = st.tabs(["Por usuario", "Por fecha"])

    with tab_users:
        user_df = pd.DataFrame(metrics.by_user)
        if user_df.empty:
            st.info("No existen registros para los filtros seleccionados.")
        else:
            if "USUARIO" in user_df.columns and "REGISTROS" in user_df.columns:
                fig = px.bar(user_df, x="USUARIO", y="REGISTROS", color="USUARIO", color_discrete_sequence=["#1565C0"])
                fig.update_layout(
                    height=350,
                    margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                    font=dict(color="#1A2A45"),
                    yaxis=dict(gridcolor="#EDF1F7"),
                    xaxis=dict(gridcolor="#EDF1F7"),
                    showlegend=False,
                )
                fig.update_xaxes(tickangle=-35)
                st.plotly_chart(fig, use_container_width=True)
            display_df = user_df.copy()
            if "TIEMPO_HORAS" in display_df.columns:
                display_df["TIEMPO"] = display_df["TIEMPO_HORAS"].apply(_format_horas)
                display_df = display_df.drop(columns=["TIEMPO_HORAS"])
            st.dataframe(display_df, use_container_width=True)

    with tab_dates:
        date_df = pd.DataFrame(metrics.by_date)
        if date_df.empty:
            st.info("No existen registros para los filtros seleccionados.")
        else:
            if "DATE" in date_df.columns and "REGISTROS" in date_df.columns:
                fig = px.area(date_df, x="DATE", y="REGISTROS", markers=True)
                fig.update_traces(
                    line=dict(color="#1565C0", width=2),
                    marker=dict(size=5, color="#1565C0"),
                    fillcolor="rgba(21,101,192,.10)",
                    hovertemplate="Fecha: %{x}<br>Registros: %{y:,.0f}<extra></extra>",
                )
                fig.update_layout(
                    height=350,
                    margin=dict(l=10, r=10, t=10, b=10),
                    xaxis_title=None,
                    yaxis_title=None,
                    font=dict(color="#1A2A45"),
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                    yaxis=dict(gridcolor="#EDF1F7", zerolinecolor="#EDF1F7"),
                    xaxis=dict(gridcolor="#EDF1F7"),
                )
                st.plotly_chart(fig, use_container_width=True)
            st.dataframe(date_df, use_container_width=True)


