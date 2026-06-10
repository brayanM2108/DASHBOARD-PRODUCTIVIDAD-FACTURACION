"""
Billing tab
===========
UI to visualize and analyze electronic billing productivity.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from frontend.components.components import (
    create_download_button,
    show_dataframe,
    show_info_message,
)
from frontend.components.filters import (
    render_agreement_filter,
    render_single_select,
)
from frontend.services.billing_service import ElectronicBillingFrontendService
from frontend.exceptions import ApiException

ALL_OPTION = "Todos"
KEY_PREFIX = "billing_v2"
GOLEMAN_COLORS = ["#0D2B5E", "#1565C0", "#F57C00", "#2E7D32", "#5A6A84"]


def _format_compact_money(value: float) -> str:
    if abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:,.1f}B"
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.1f}M"
    return f"${value:,.0f}"


def _get_date_bounds(df: pd.DataFrame, date_col: str | None) -> tuple[pd.Timestamp, pd.Timestamp]:
    if not date_col or date_col not in df.columns:
        today = pd.Timestamp.now().normalize()
        return today, today

    dates = pd.to_datetime(df[date_col], errors="coerce").dropna()
    if dates.empty:
        today = pd.Timestamp.now().normalize()
        return today, today

    return dates.min(), dates.max()


def _plot_value_by_user(df: pd.DataFrame, user_col: str) -> None:
    if df.empty:
        show_info_message("No hay datos para graficar por usuario.")
        return

    chart_df = df.copy()
    chart_df["VALOR_TERCERO"] = pd.to_numeric(chart_df["VALOR_TERCERO"], errors="coerce").fillna(0)
    chart_df = chart_df.sort_values("VALOR_TERCERO", ascending=False).head(12)

    fig = px.bar(
        chart_df,
        x=user_col,
        y="VALOR_TERCERO",
        text="VALOR_TERCERO",
        color=user_col,
        color_discrete_sequence=GOLEMAN_COLORS,
    )
    fig.update_traces(
        texttemplate="$%{y:,.0f}",
        textposition="outside",
        hovertemplate="%{x}<br>Valor tercero: $%{y:,.0f}<extra></extra>",
    )
    fig.update_layout(
        height=340,
        showlegend=False,
        margin=dict(l=10, r=10, t=8, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_title=None,
        yaxis_title=None,
        font=dict(color="#1A2A45"),
    )
    fig.update_xaxes(tickangle=-35, type="category")
    fig.update_yaxes(tickformat=",.0f", gridcolor="#EDF1F7")
    st.plotly_chart(fig, width="stretch")


def _plot_distribution(df: pd.DataFrame, user_col: str) -> None:
    if df.empty:
        show_info_message("No hay datos para distribución.")
        return

    chart_df = df.copy()
    chart_df["VALOR_TERCERO"] = pd.to_numeric(chart_df["VALOR_TERCERO"], errors="coerce").fillna(0)
    chart_df = chart_df.sort_values("VALOR_TERCERO", ascending=False).head(6)

    fig = px.pie(
        chart_df,
        names=user_col,
        values="VALOR_TERCERO",
        hole=0.58,
        color_discrete_sequence=GOLEMAN_COLORS,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate="%{label}<br>$%{value:,.0f}<extra></extra>",
    )
    fig.update_layout(
        height=340,
        margin=dict(l=0, r=0, t=8, b=0),
        legend=dict(orientation="h", y=-0.1),
        paper_bgcolor="white",
        font=dict(color="#1A2A45"),
    )
    st.plotly_chart(fig, width="stretch")


def _plot_trend(df: pd.DataFrame) -> None:
    if df.empty:
        show_info_message("No hay datos para graficar por fecha.")
        return

    chart_df = df.copy()
    chart_df["DATE"] = pd.to_datetime(chart_df["DATE"], errors="coerce")
    chart_df["VALOR_TERCERO"] = pd.to_numeric(chart_df["VALOR_TERCERO"], errors="coerce").fillna(0)
    chart_df = chart_df.dropna(subset=["DATE"]).sort_values("DATE")

    fig = px.area(
        chart_df,
        x="DATE",
        y="VALOR_TERCERO",
        markers=True,
        color_discrete_sequence=["#1565C0"],
    )
    fig.update_traces(
        line=dict(width=2, color="#1565C0"),
        fillcolor="rgba(21,101,192,.10)",
        hovertemplate="%{x|%d/%m/%Y}<br>Valor: $%{y:,.0f}<extra></extra>",
    )
    fig.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=8, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_title=None,
        yaxis_title=None,
        font=dict(color="#1A2A45"),
    )
    fig.update_yaxes(tickformat=",.0f", gridcolor="#EDF1F7")
    st.plotly_chart(fig, width="stretch")


def _build_user_detail_table(
    df_by_user: pd.DataFrame,
    user_col: str,
) -> pd.DataFrame:
    if df_by_user.empty:
        return pd.DataFrame()

    table_df = df_by_user.copy()
    table_df["REGISTROS"] = pd.to_numeric(table_df.get("REGISTROS"), errors="coerce").fillna(0).astype(int)
    table_df["VALOR_TERCERO"] = pd.to_numeric(table_df.get("VALOR_TERCERO"), errors="coerce").fillna(0)
    table_df["VALOR TERCERO"] = table_df["VALOR_TERCERO"].map(lambda v: f"${v:,.0f}")

    return (
        table_df[[user_col, "REGISTROS", "VALOR TERCERO"]]
        .rename(columns={user_col: "USUARIO"})
        .sort_values("REGISTROS", ascending=False)
        .reset_index(drop=True)
    )


def _section_title(label: str) -> None:
    st.markdown(f'<div class="g-section-title">{label}</div>', unsafe_allow_html=True)


def render_tab_billing_electronic():
    """Render the billing V2 tab."""
    render_billing_electronic_section()


def render_billing_electronic_section():
    """Render billing section based only on electronic billing."""
    e_billing_df = st.session_state.get("electronic_billing_df")

    if e_billing_df is None or e_billing_df.empty:
        show_info_message("No hay datos de facturación electrónica. Carga un archivo en la sección de carga.")
        return

    user_col = next((c for c in ["USUARIO", "USUARIO FACTURO", "USUARIO FACTUR"] if c in e_billing_df.columns), None)
    date_col = next((c for c in ["FECHA FACTURA", "FECHA", "FECHA_SERVICIO"] if c in e_billing_df.columns), None)
    agreement_col = next((c for c in ["CONVENIO"] if c in e_billing_df.columns), None)

    st.markdown(
        """
        <div class="g-tab-header">
          <div class="g-tab-header-title"><span>▣</span>Productividad · Facturación electrónica</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="g-section">', unsafe_allow_html=True)
    _section_title("Filtros")
    col1, col2, col3, col4 = st.columns(4)
    min_date, max_date = _get_date_bounds(e_billing_df, date_col)
    with col1:
        start_date = st.date_input(
            "Fecha inicio",
            value=min_date.date(),
            key=f"{KEY_PREFIX}_start_date",
        )
    with col2:
        end_date = st.date_input(
            "Fecha fin",
            value=max_date.date(),
            key=f"{KEY_PREFIX}_end_date",
        )

    users_list = [ALL_OPTION]
    if user_col and user_col in e_billing_df.columns:
        users_list = [ALL_OPTION] + sorted(
            e_billing_df[user_col].dropna().astype(str).str.strip().replace("", pd.NA).dropna().unique().tolist()
        )

    agreement_list = [ALL_OPTION]
    if agreement_col and agreement_col in e_billing_df.columns:
        agreement_list = [ALL_OPTION] + sorted(
            e_billing_df[agreement_col].dropna().astype(str).str.strip().replace("", pd.NA).dropna().unique().tolist()
        )

    with col3:
        agreement_sel = render_agreement_filter(agreement_list, key_prefix=KEY_PREFIX)
    with col4:
        usuario_sel = render_single_select("Usuario", users_list, key=f"{KEY_PREFIX}_usuario")
    st.markdown("</div>", unsafe_allow_html=True)

    selected_agreement = None if agreement_sel == ALL_OPTION else agreement_sel
    selected_users = None if usuario_sel == ALL_OPTION else [usuario_sel]

    token = st.session_state.get("token")
    if not token:
        show_info_message("Debes iniciar sesión para ver la facturación.")
        return

    try:
        service = ElectronicBillingFrontendService(token=token)
        metrics = service.get_metrics(
            start_date=start_date,
            end_date=end_date,
            selected_users=selected_users,
            selected_agreement=selected_agreement,
        )
    except ApiException as e:
        st.warning(str(e))
        return

    df_by_user = pd.DataFrame([r.__dict__ for r in metrics.by_user])
    df_by_date = pd.DataFrame([r.__dict__ for r in metrics.by_date])
    result_user_col = "USUARIO" if "USUARIO" in df_by_user.columns else (df_by_user.columns[0] if not df_by_user.empty else "USUARIO")

    st.markdown('<div class="g-section">', unsafe_allow_html=True)
    _section_title("Métricas del período")
    k1, k2, k3, k4 = st.columns(4)
    total_registros = metrics.total_records
    total_valor = metrics.total_valor_tercero
    active_users = int(df_by_user[result_user_col].nunique()) if result_user_col in df_by_user.columns else 0
    avg_per_user = int(total_registros / active_users) if active_users else 0

    with k1:
        st.metric("Total registros", f"{total_registros:,}")
    with k2:
        st.metric("Valor tercero", _format_compact_money(total_valor))
    with k3:
        st.metric("Usuarios activos", f"{active_users:,}")
    with k4:
        st.metric("Promedio / usuario", f"{avg_per_user:,}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="g-section">', unsafe_allow_html=True)
    _section_title("Valor facturado por usuario")
    chart_col, dist_col = st.columns([2, 1])
    with chart_col:
        st.markdown('<div class="g-chart-card"><div class="g-muted-note">Valor acumulado por usuario</div>', unsafe_allow_html=True)
        _plot_value_by_user(df_by_user, result_user_col)
        st.markdown("</div>", unsafe_allow_html=True)
    with dist_col:
        st.markdown('<div class="g-chart-card"><div class="g-muted-note">Distribución</div>', unsafe_allow_html=True)
        _plot_distribution(df_by_user, result_user_col)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="g-section">', unsafe_allow_html=True)
    _section_title("Detalle por usuario")
    detail_df = _build_user_detail_table(df_by_user, result_user_col)
    if detail_df.empty:
        show_info_message("No hay detalle por usuario para mostrar.")
    else:
        st.dataframe(detail_df, width="stretch", hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="g-section">', unsafe_allow_html=True)
    _section_title("Tendencia por fecha")
    st.markdown('<div class="g-chart-card"><div class="g-muted-note">Valor facturado acumulado</div>', unsafe_allow_html=True)
    _plot_trend(df_by_date)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
