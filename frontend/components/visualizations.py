"""
Visualizations and Graphs
===========================
Functions for creating graphs with Plotly and Matplotlib.

Interactive click-to-filter:
  - Each function accepts an optional `view_key` to enable interactivity.
  - Clicking a chart element stores the clicked category in
    st.session_state["_viz_filter_{view_key}"].
  - The view layer can read this filter to update other charts/tables.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from ui.goleman_theme import GolemanTheme


# ══════════════════════════════════════════════
#  INTERACTIVE FILTER INFRASTRUCTURE
# ══════════════════════════════════════════════

def set_viz_filter(view_key: str, value: str) -> None:
    """Store a click-based filter for a view namespace."""
    st.session_state[f"_viz_filter_{view_key}"] = value


def get_viz_filter(view_key: str) -> str | None:
    """Read the active filter for a view namespace, if any."""
    return st.session_state.get(f"_viz_filter_{view_key}")


def clear_viz_filter(view_key: str) -> None:
    """Remove the active filter for a view namespace."""
    st.session_state.pop(f"_viz_filter_{view_key}", None)


def any_viz_filter_active(view_key: str) -> bool:
    """Check whether a filter is currently active."""
    return f"_viz_filter_{view_key}" in st.session_state


def _render_interactive_chart(fig: go.Figure, key: str, view_key: str | None) -> str | None:
    """Render a Plotly chart and capture click events into session state.

    Returns the clicked value (label / x category) when a click just happened,
    or the *currently active* filter value, or None.
    """
    if view_key is None:
        st.plotly_chart(fig, use_container_width=True)
        return None

    fig.update_layout(clickmode="event+select", dragmode=False)

    event = st.plotly_chart(fig, key=key, on_select="rerun", use_container_width=True)

    # Try to extract a fresh click from the selection event
    clicked: str | None = None
    try:
        if event is not None:
            sel = getattr(event, "selection", None)
            if isinstance(sel, dict):
                points = sel.get("points") or []
            else:
                points = getattr(sel, "points", []) if sel is not None else []

            if points:
                raw = points[0]
                if isinstance(raw, dict):
                    clicked = raw.get("label") or str(raw.get("x", "")) or str(raw.get("y", ""))
                elif hasattr(raw, "label"):
                    clicked = raw.label
                elif hasattr(raw, "x"):
                    clicked = str(raw.x)
    except Exception:
        pass

    if clicked:
        set_viz_filter(view_key, clicked)

    return get_viz_filter(view_key)


# ══════════════════════════════════════════════
#  GENERAL PURPOSE CHARTS
# ══════════════════════════════════════════════

def plot_bar_chart(df, x_col, y_col, title, color=None, sortable=True, sort_key=None, view_key=None):
    if df is None or df.empty:
        st.info("No hay datos para graficar.")
        return

    # Apply active filter if any
    active = get_viz_filter(view_key) if view_key else None
    if active:
        for col in [x_col, color] if color else [x_col]:
            if col and col in df.columns:
                df = df[df[col].astype(str).str.strip().str.lower() == active.strip().lower()]
        if df.empty:
            st.info(f"No hay datos para el filtro: {active}")
            return

    df_plot = df.copy()

    if sortable:
        col1, col2 = st.columns([3, 1])
        with col2:
            sort_key_suffix = f"_{sort_key}" if sort_key else ""
            orden = st.selectbox(
                "Ordenar por:",
                options=["Sin ordenar", "Mayor a Menor", "Menor a Mayor"],
                key=f"sort_bar{sort_key_suffix}",
                index=1,
            )
            if orden == "Mayor a Menor":
                df_plot = df_plot.sort_values(by=y_col, ascending=False)
            elif orden == "Menor a Mayor":
                df_plot = df_plot.sort_values(by=y_col, ascending=True)

    df_plot[x_col] = df_plot[x_col].astype(str)

    fig = px.bar(df_plot, x=x_col, y=y_col, title=title, color=color, text=y_col)
    fig.update_traces(
        texttemplate="%{y:,.0f}",
        textposition="outside",
        hovertemplate="%{x}<br>Valor: %{y:,.0f}<extra></extra>",
    )
    fig.update_yaxes(tickformat=",.0f", separatethousands=True)
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=True if color else False,
        xaxis_type="category",
    )
    _render_interactive_chart(fig, f"bar_{sort_key or id(df)}", view_key)


def plot_line_chart(df, x_col, y_col, title, color=None, sortable=True, sort_key=None, view_key=None):
    if df is None or df.empty:
        st.info("No hay datos para graficar.")
        return

    active = get_viz_filter(view_key) if view_key else None
    if active:
        for col in [x_col, color] if color else [x_col]:
            if col and col in df.columns:
                df = df[df[col].astype(str).str.strip().str.lower() == active.strip().lower()]
        if df.empty:
            st.info(f"No hay datos para el filtro: {active}")
            return

    df_plot = df.copy()

    if sortable:
        col1, col2 = st.columns([3, 1])
        with col2:
            sort_key_suffix = f"_{sort_key}" if sort_key else ""
            orden = st.selectbox(
                "Ordenar por:",
                options=["Por Fecha", "Mayor a Menor", "Menor a Mayor"],
                key=f"sort_line{sort_key_suffix}",
            )
            if orden == "Mayor a Menor":
                df_plot = df_plot.sort_values(by=y_col, ascending=False)
            elif orden == "Menor a Mayor":
                df_plot = df_plot.sort_values(by=y_col, ascending=True)
            else:
                df_plot = df_plot.sort_values(by=x_col)

    fig = px.line(df_plot, x=x_col, y=y_col, title=title, color=color, markers=True)
    fig.update_traces(hovertemplate="%{x}<br>Valor: %{y:,.0f}<extra></extra>")
    fig.update_yaxes(tickformat=",.0f", separatethousands=True)
    fig.update_layout(xaxis_tickangle=-45)
    _render_interactive_chart(fig, f"line_{sort_key or id(df)}", view_key)


def plot_metrics_summary(metrics):
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Registros", f"{metrics.get('total', 0):,}")
    with col2:
        promedio = metrics.get("daily_average", 0)
        st.metric("Promedio Diario", f"{promedio:.2f}")


def plot_productivity_charts(metrics, tipo="Productividad"):
    st.subheader(f"📊 Análisis de {tipo}")
    plot_metrics_summary(metrics)

    if metrics.get("by_user") is not None and not metrics["by_user"].empty:
        st.markdown("### Por Usuario")
        plot_bar_chart(
            metrics["by_user"],
            x_col=metrics["by_user"].columns[0],
            y_col="COUNT",
            title=f"{tipo} por Usuario",
            sortable=True,
            sort_key=f"{tipo}_usuario",
        )

    if metrics.get("by_date") is not None and not metrics["by_date"].empty:
        st.markdown("### Por Fecha")
        plot_line_chart(
            metrics["by_date"],
            x_col="DATE",
            y_col="COUNT",
            title=f"{tipo} por Fecha",
            sortable=True,
            sort_key=f"{tipo}_fecha",
        )


# ══════════════════════════════════════════════
#  RADICACIÓN
# ══════════════════════════════════════════════

_RAD_COLOR_DENTRO = GolemanTheme.SUCCESS
_RAD_COLOR_PROXIMO = GolemanTheme.ORANGE
_RAD_COLOR_VENCIDO = GolemanTheme.DANGER


def plot_rad_donut(dentro: int, proximas: int, vencidas: int, view_key=None):
    labels = ["Dentro SLA", "Próximas a vencer", "Vencidas"]
    values = [dentro, proximas, vencidas]
    colors = [_RAD_COLOR_DENTRO, _RAD_COLOR_PROXIMO, _RAD_COLOR_VENCIDO]

    fig = go.Figure(data=[
        go.Pie(
            labels=labels, values=values, hole=0.55,
            marker=dict(colors=colors),
            textinfo="label+percent",
            textfont=dict(size=11, color=GolemanTheme.TEXT),
            hovertemplate="%{label}<br>%{value:,} facturas<br>%{percent}<extra></extra>",
        )
    ])
    fig.update_layout(
        height=300, margin=dict(l=10, r=10, t=10, b=10),
        showlegend=True,
        legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center", font=dict(size=11, color=GolemanTheme.TEXT)),
        font=dict(color=GolemanTheme.TEXT),
        paper_bgcolor="white", plot_bgcolor="white",
    )
    _render_interactive_chart(fig, "rad_donut", view_key)


def plot_rad_vencidas_por_dia(df_radicacion, view_key=None):
    if df_radicacion is None or df_radicacion.empty:
        st.info("No hay datos para la tendencia temporal.")
        return

    active = get_viz_filter(view_key) if view_key else None
    df = df_radicacion.copy()
    if active:
        try:
            active_date = pd.to_datetime(active).date()
            df = df[df["VENCIDA"] == True] if "VENCIDA" in df.columns else df
            fecha_col = next((c for c in ["FECHA FACTURA"] if c in df.columns), None)
            if fecha_col:
                df["FECHA"] = pd.to_datetime(df[fecha_col], errors="coerce").dt.date
                df = df[df["FECHA"] == active_date]
        except Exception:
            pass

    vencidas_df = df[df["VENCIDA"] == True].copy() if "VENCIDA" in df.columns else df[df.index >= 0].copy()
    if vencidas_df.empty:
        st.info("No hay facturas vencidas para graficar la tendencia.")
        return

    fecha_col = next((c for c in ["FECHA FACTURA"] if c in vencidas_df.columns), None)
    if not fecha_col:
        return

    vencidas_df["FECHA"] = vencidas_df[fecha_col].dt.date
    daily = vencidas_df.groupby("FECHA").size().reset_index(name="Vencidas")
    daily = daily.sort_values("FECHA")

    fig = px.area(daily, x="FECHA", y="Vencidas", markers=True)
    fig.update_traces(
        line=dict(color=_RAD_COLOR_VENCIDO, width=2),
        marker=dict(size=5, color=_RAD_COLOR_VENCIDO),
        fillcolor="rgba(229,62,62,.10)",
        hovertemplate="Fecha: %{x}<br>Vencidas: %{y:,.0f}<extra></extra>",
    )
    fig.update_layout(
        height=300, margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title=None, yaxis_title="Facturas vencidas",
        yaxis_title_font=dict(color=GolemanTheme.MUTED, size=11),
        font=dict(color=GolemanTheme.TEXT, size=11),
        paper_bgcolor="white", plot_bgcolor="white",
        yaxis=dict(gridcolor="#EDF1F7", zerolinecolor="#EDF1F7"),
        xaxis=dict(gridcolor="#EDF1F7"),
    )
    _render_interactive_chart(fig, "rad_vencidas", view_key)


def plot_rad_top_usuarios(df_by_user, top_n: int = 5, view_key=None):
    if df_by_user is None or df_by_user.empty:
        st.info("No hay datos por usuario.")
        return

    active = get_viz_filter(view_key) if view_key else None
    df = df_by_user.copy()
    if active:
        if "USUARIO" in df.columns:
            df = df[df["USUARIO"].astype(str).str.strip().str.lower() == active.strip().lower()]
        if df.empty:
            st.info(f"No hay datos para el filtro: {active}")
            return

    df_sorted = df.sort_values("VENCIDAS", ascending=True).tail(top_n)

    fig = go.Figure(data=[
        go.Bar(
            y=df_sorted["USUARIO"],
            x=df_sorted["VENCIDAS"],
            orientation="h",
            marker=dict(
                color=[_RAD_COLOR_VENCIDO if v > 0 else _RAD_COLOR_DENTRO for v in df_sorted["VENCIDAS"]],
                cornerradius=4,
            ),
            text=df_sorted["VENCIDAS"],
            textposition="outside",
            hovertemplate="%{y}<br>Vencidas: %{x:,.0f}<extra></extra>",
        )
    ])
    fig.update_layout(
        height=300, margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Facturas vencidas",
        xaxis_title_font=dict(color=GolemanTheme.MUTED, size=11),
        yaxis_title=None,
        font=dict(color=GolemanTheme.TEXT, size=11),
        paper_bgcolor="white", plot_bgcolor="white",
        xaxis=dict(gridcolor=GolemanTheme.BORDER, zerolinecolor=GolemanTheme.BORDER),
        yaxis=dict(gridcolor=GolemanTheme.BORDER),
        showlegend=False,
    )
    _render_interactive_chart(fig, "rad_top_usuarios", view_key)


def plot_rad_distribucion_antiguedad(df_radicacion, view_key=None):
    if df_radicacion is None or df_radicacion.empty:
        st.info("No hay datos para la distribución por antigüedad.")
        return

    active = get_viz_filter(view_key) if view_key else None
    pendientes = df_radicacion[df_radicacion["RADICADO"] == False].copy()

    if active:
        bins = [0, 3, 6, 11, 999]
        labels = ["0-2 días", "3-5 días", "6-10 días", "Más de 10 días"]
        if active in labels:
            idx = labels.index(active)
            lo, hi = bins[idx], bins[idx + 1]
            pendientes = pendientes[(pendientes["DIAS_SIN_RADICAR"] > lo) & (pendientes["DIAS_SIN_RADICAR"] <= hi)]
        if pendientes.empty:
            st.info(f"No hay facturas pendientes en el rango: {active}")
            return

    if pendientes.empty:
        st.info("No hay facturas pendientes para graficar.")
        return

    bins = [0, 3, 6, 11, 999]
    labels = ["0-2 días", "3-5 días", "6-10 días", "Más de 10 días"]
    colors_bins = [_RAD_COLOR_DENTRO, _RAD_COLOR_PROXIMO, GolemanTheme.WARNING, _RAD_COLOR_VENCIDO]

    pendientes["ANTIGUEDAD_GROUP"] = pd.cut(
        pendientes["DIAS_SIN_RADICAR"], bins=bins, labels=labels, right=True
    )
    dist = pendientes.groupby("ANTIGUEDAD_GROUP", observed=True).size().reset_index(name="Cantidad")

    for label in labels:
        if label not in dist["ANTIGUEDAD_GROUP"].values:
            dist = pd.concat([dist, pd.DataFrame({"ANTIGUEDAD_GROUP": [label], "Cantidad": [0]})], ignore_index=True)

    dist = dist.sort_values("ANTIGUEDAD_GROUP", key=lambda x: pd.Categorical(x, categories=labels, ordered=True))
    dist["Cantidad"] = dist["Cantidad"].astype(int)

    fig = go.Figure(data=[
        go.Pie(
            labels=dist["ANTIGUEDAD_GROUP"],
            values=dist["Cantidad"],
            hole=0.55,
            marker=dict(colors=colors_bins),
            textinfo="label+percent",
            textfont=dict(size=11, color=GolemanTheme.TEXT),
            hovertemplate="%{label}<br>%{value:,} facturas (%{percent})<extra></extra>",
        )
    ])
    fig.update_layout(
        height=300, margin=dict(l=10, r=10, t=10, b=10),
        showlegend=True,
        legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center", font=dict(size=11, color=GolemanTheme.TEXT)),
        font=dict(color=GolemanTheme.TEXT),
        paper_bgcolor="white", plot_bgcolor="white",
    )
    _render_interactive_chart(fig, "rad_antiguedad", view_key)


# ══════════════════════════════════════════════
#  FACTURACIÓN ELECTRÓNICA
# ══════════════════════════════════════════════

_GOLEMAN_COLORS = ["#0D2B5E", "#1565C0", "#F57C00", "#2E7D32", "#5A6A84"]


def plot_billing_value_by_user(df: pd.DataFrame, user_col: str, view_key=None):
    if df.empty:
        st.info("No hay datos para graficar por usuario.")
        return

    active = get_viz_filter(view_key) if view_key else None
    chart_df = df.copy()
    if active and user_col in chart_df.columns:
        chart_df = chart_df[chart_df[user_col].astype(str).str.strip().str.lower() == active.strip().lower()]
        if chart_df.empty:
            st.info(f"No hay datos para el filtro: {active}")
            return

    chart_df["VALOR_TERCERO"] = pd.to_numeric(chart_df["VALOR_TERCERO"], errors="coerce").fillna(0)
    chart_df = chart_df.sort_values("VALOR_TERCERO", ascending=True)
    cats = chart_df[user_col].tolist()
    chart_df[user_col] = pd.Categorical(chart_df[user_col], categories=cats, ordered=True)

    fig = px.bar(
        chart_df, x="VALOR_TERCERO", y=user_col,
        text="VALOR_TERCERO", color=user_col, orientation="h",
        color_discrete_sequence=_GOLEMAN_COLORS,
        category_orders={user_col: cats},
    )
    fig.update_traces(
        texttemplate="$%{x:,.0f}", textposition="outside",
        hovertemplate="%{y}<br>Valor tercero: $%{x:,.0f}<extra></extra>",
    )
    fig.update_layout(
        height=340, showlegend=False,
        margin=dict(l=10, r=80, t=8, b=10),
        plot_bgcolor=GolemanTheme.WHITE, paper_bgcolor=GolemanTheme.WHITE,
        xaxis_title=None, yaxis_title=None,
        font=dict(color=GolemanTheme.TEXT, size=11),
    )
    fig.update_xaxes(tickformat=",.0f", gridcolor=GolemanTheme.BORDER)
    fig.update_yaxes(gridcolor=GolemanTheme.BORDER)
    _render_interactive_chart(fig, "bill_valor_user", view_key)


def plot_billing_distribution(df: pd.DataFrame, user_col: str, view_key=None):
    if df.empty:
        st.info("No hay datos para distribución.")
        return

    active = get_viz_filter(view_key) if view_key else None
    chart_df = df.copy()
    if active and user_col in chart_df.columns:
        chart_df = chart_df[chart_df[user_col].astype(str).str.strip().str.lower() == active.strip().lower()]
        if chart_df.empty:
            st.info(f"No hay datos para el filtro: {active}")
            return

    chart_df["VALOR_TERCERO"] = pd.to_numeric(chart_df["VALOR_TERCERO"], errors="coerce").fillna(0)
    chart_df = chart_df.sort_values("VALOR_TERCERO", ascending=False)

    fig = px.pie(
        chart_df, names=user_col, values="VALOR_TERCERO", hole=0.58,
        color_discrete_sequence=_GOLEMAN_COLORS,
    )
    fig.update_traces(
        textposition="inside", textinfo="percent",
        hovertemplate="%{label}<br>$%{value:,.0f}<extra></extra>",
    )
    fig.update_layout(
        height=340, margin=dict(l=0, r=0, t=8, b=0),
        legend=dict(orientation="h", y=-0.1),
        paper_bgcolor="white", font=dict(color="#1A2A45"),
    )
    _render_interactive_chart(fig, "bill_distrib", view_key)


def plot_billing_records_by_user(df: pd.DataFrame, user_col: str, view_key=None):
    if df.empty:
        st.info("No hay datos para graficar por usuario.")
        return

    active = get_viz_filter(view_key) if view_key else None
    chart_df = df.copy()
    if active and user_col in chart_df.columns:
        chart_df = chart_df[chart_df[user_col].astype(str).str.strip().str.lower() == active.strip().lower()]
        if chart_df.empty:
            st.info(f"No hay datos para el filtro: {active}")
            return

    chart_df["REGISTROS"] = pd.to_numeric(chart_df["REGISTROS"], errors="coerce").fillna(0).astype(int)
    chart_df = chart_df.sort_values("REGISTROS", ascending=True)
    cats = chart_df[user_col].tolist()
    chart_df[user_col] = pd.Categorical(chart_df[user_col], categories=cats, ordered=True)

    fig = px.bar(
        chart_df, x="REGISTROS", y=user_col,
        text="REGISTROS", color=user_col, orientation="h",
        color_discrete_sequence=_GOLEMAN_COLORS,
        category_orders={user_col: cats},
    )
    fig.update_traces(
        texttemplate="%{x:,.0f}", textposition="outside",
        hovertemplate="%{y}<br>Registros: %{x:,.0f}<extra></extra>",
    )
    fig.update_layout(
        height=340, showlegend=False,
        margin=dict(l=10, r=60, t=8, b=10),
        plot_bgcolor=GolemanTheme.WHITE, paper_bgcolor=GolemanTheme.WHITE,
        xaxis_title=None, yaxis_title=None,
        font=dict(color=GolemanTheme.TEXT, size=11),
    )
    fig.update_xaxes(tickformat=",.0f", gridcolor=GolemanTheme.BORDER)
    fig.update_yaxes(gridcolor=GolemanTheme.BORDER)
    _render_interactive_chart(fig, "bill_records_user", view_key)


def plot_billing_records_distribution(df: pd.DataFrame, user_col: str, view_key=None):
    if df.empty:
        st.info("No hay datos para distribución.")
        return

    active = get_viz_filter(view_key) if view_key else None
    chart_df = df.copy()
    if active and user_col in chart_df.columns:
        chart_df = chart_df[chart_df[user_col].astype(str).str.strip().str.lower() == active.strip().lower()]
        if chart_df.empty:
            st.info(f"No hay datos para el filtro: {active}")
            return

    chart_df["REGISTROS"] = pd.to_numeric(chart_df["REGISTROS"], errors="coerce").fillna(0).astype(int)
    chart_df = chart_df.sort_values("REGISTROS", ascending=False)

    fig = px.pie(
        chart_df, names=user_col, values="REGISTROS", hole=0.58,
        color_discrete_sequence=_GOLEMAN_COLORS,
    )
    fig.update_traces(
        textposition="inside", textinfo="percent",
        hovertemplate="%{label}<br>%{value:,} registros<extra></extra>",
    )
    fig.update_layout(
        height=340, margin=dict(l=0, r=0, t=8, b=0),
        legend=dict(orientation="h", y=-0.1),
        paper_bgcolor="white", font=dict(color="#1A2A45"),
    )
    _render_interactive_chart(fig, "bill_records_distrib", view_key)


def plot_billing_trend(df: pd.DataFrame, view_key=None):
    if df.empty:
        st.info("No hay datos para graficar por fecha.")
        return

    chart_df = df.copy()
    chart_df["DATE"] = pd.to_datetime(chart_df["DATE"], errors="coerce")
    chart_df["VALOR_TERCERO"] = pd.to_numeric(chart_df["VALOR_TERCERO"], errors="coerce").fillna(0)

    active = get_viz_filter(view_key) if view_key else None
    if active:
        try:
            active_dt = pd.to_datetime(active).date()
            chart_df = chart_df[chart_df["DATE"].dt.date == active_dt]
        except Exception:
            chart_df = chart_df[chart_df["DATE"].astype(str).str.contains(active, na=False)]
        if chart_df.empty:
            st.info(f"No hay datos para el filtro: {active}")
            return

    chart_df = chart_df.dropna(subset=["DATE"]).sort_values("DATE")

    fig = px.area(
        chart_df, x="DATE", y="VALOR_TERCERO",
        markers=True, color_discrete_sequence=["#1565C0"],
    )
    fig.update_traces(
        line=dict(width=2, color="#1565C0"),
        fillcolor="rgba(21,101,192,.10)",
        hovertemplate="%{x|%d/%m/%Y}<br>Valor: $%{y:,.0f}<extra></extra>",
    )
    fig.update_layout(
        height=300, margin=dict(l=10, r=10, t=8, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis_title=None, yaxis_title=None,
        font=dict(color="#1A2A45"),
    )
    fig.update_yaxes(tickformat=",.0f", gridcolor="#EDF1F7")
    _render_interactive_chart(fig, "bill_trend", view_key)


def plot_billing_records_trend(df: pd.DataFrame, view_key=None):
    if df.empty:
        st.info("No hay datos para graficar por fecha.")
        return

    chart_df = df.copy()
    chart_df["DATE"] = pd.to_datetime(chart_df["DATE"], errors="coerce")
    chart_df["REGISTROS"] = pd.to_numeric(chart_df["REGISTROS"], errors="coerce").fillna(0).astype(int)

    active = get_viz_filter(view_key) if view_key else None
    if active:
        try:
            active_dt = pd.to_datetime(active).date()
            chart_df = chart_df[chart_df["DATE"].dt.date == active_dt]
        except Exception:
            chart_df = chart_df[chart_df["DATE"].astype(str).str.contains(active, na=False)]
        if chart_df.empty:
            st.info(f"No hay datos para el filtro: {active}")
            return

    chart_df = chart_df.dropna(subset=["DATE"]).sort_values("DATE")

    fig = px.area(
        chart_df, x="DATE", y="REGISTROS",
        markers=True, color_discrete_sequence=["#F97838"],
    )
    fig.update_traces(
        line=dict(width=2, color="#F97838"),
        fillcolor="rgba(249,120,56,.10)",
        hovertemplate="%{x|%d/%m/%Y}<br>Registros: %{y:,.0f}<extra></extra>",
    )
    fig.update_layout(
        height=300, margin=dict(l=10, r=10, t=8, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis_title=None, yaxis_title=None,
        font=dict(color="#1A2A45"),
    )
    fig.update_yaxes(tickformat=",.0f", gridcolor="#EDF1F7")
    _render_interactive_chart(fig, "bill_records_trend", view_key)


# ══════════════════════════════════════════════
#  FACTURACIÓN MANUAL (Procesos Administrativos)
# ══════════════════════════════════════════════

def plot_manual_bar(df: pd.DataFrame, view_key=None):
    if df is None or df.empty:
        st.info("No hay datos para el gráfico de barras.")
        return

    active = get_viz_filter(view_key) if view_key else None
    chart_df = df.copy()
    if active:
        for col in ["NOMBRE", "PROCESO"]:
            if col in chart_df.columns:
                chart_df = chart_df[chart_df[col].astype(str).str.strip().str.lower() == active.strip().lower()]
                if not chart_df.empty:
                    break
        if chart_df.empty:
            st.info(f"No hay datos para el filtro: {active}")
            return

    try:
        fig = px.bar(chart_df, x="NOMBRE", y="CANTIDAD", color="CANTIDAD", color_continuous_scale="Blues")
        fig.update_layout(xaxis_tickangle=-45)
        _render_interactive_chart(fig, "manual_bar", view_key)
    except Exception as e:
        st.warning(f"Error en gráfico de barras: {e}")


def plot_manual_pie(df: pd.DataFrame, mode: str, view_key=None):
    if df is None or df.empty:
        st.info("No hay datos para el gráfico de torta.")
        return

    active = get_viz_filter(view_key) if view_key else None
    chart_df = df.copy()
    name_col = "NOMBRE" if mode == "person" else "PROCESO"
    if active and name_col in chart_df.columns:
        chart_df = chart_df[chart_df[name_col].astype(str).str.strip().str.lower() == active.strip().lower()]
        if chart_df.empty:
            st.info(f"No hay datos para el filtro: {active}")
            return

    try:
        if mode == "person":
            fig = px.pie(chart_df, values="CANTIDAD", names="NOMBRE", hole=0.4)
        else:
            fig = px.pie(chart_df, values="CANTIDAD", names="PROCESO", hole=0.4)
        _render_interactive_chart(fig, f"manual_pie_{mode}", view_key)
    except Exception as e:
        st.warning(f"Error en gráfico de torta: {e}")


def plot_manual_trend(df: pd.DataFrame, view_key=None):
    if df is None or df.empty:
        st.info("No hay datos para la tendencia temporal.")
        return

    active = get_viz_filter(view_key) if view_key else None
    chart_df = df.copy()
    if active:
        try:
            active_dt = pd.to_datetime(active).date()
            chart_df["_FECHA"] = pd.to_datetime(chart_df["FECHA"], errors="coerce").dt.date
            chart_df = chart_df[chart_df["_FECHA"] == active_dt]
        except Exception:
            chart_df = chart_df[chart_df["FECHA"].astype(str).str.contains(active, na=False)]
        if chart_df.empty:
            st.info(f"No hay datos para el filtro: {active}")
            return

    try:
        fig = px.area(chart_df, x="FECHA", y="CANTIDAD", markers=True)
        fig.update_traces(
            line=dict(color="#1565C0", width=2),
            marker=dict(size=5, color="#1565C0"),
            fillcolor="rgba(21,101,192,.10)",
            hovertemplate="Fecha: %{x}<br>Cantidad: %{y:,.0f}<extra></extra>",
        )
        fig.update_layout(
            height=300, margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title=None, yaxis_title=None,
            font=dict(color="#1A2A45"),
            paper_bgcolor="white", plot_bgcolor="white",
            yaxis=dict(gridcolor="#EDF1F7", zerolinecolor="#EDF1F7"),
            xaxis=dict(gridcolor="#EDF1F7"),
        )
        _render_interactive_chart(fig, "manual_trend", view_key)
    except Exception as e:
        st.warning(f"Error en tendencia: {e}")


# ══════════════════════════════════════════════
#  CONVENIOS (Facturación Electrónica)
# ══════════════════════════════════════════════

def _fmt_compact(val: float) -> str:
    if abs(val) >= 1_000_000_000:
        return f"${val / 1_000_000_000:.1f}B"
    if abs(val) >= 1_000_000:
        return f"${val / 1_000_000:.1f}M"
    if abs(val) >= 1_000:
        return f"${val / 1_000:.1f}K"
    return f"${val:,.0f}"


def plot_conv_records_top10(df: pd.DataFrame, view_key=None):
    if df is None or df.empty:
        st.info("No hay datos de convenios por registros.")
        return

    active = get_viz_filter(view_key) if view_key else None
    chart_df = df.copy()
    if active and "convenio" in chart_df.columns:
        chart_df = chart_df[chart_df["convenio"].astype(str).str.strip().str.lower() == active.strip().lower()]
        if chart_df.empty:
            st.info(f"No hay datos para el filtro: {active}")
            return

    total = int(chart_df["records"].sum())
    top10 = chart_df.nlargest(10, "records").copy()
    top10["pct"] = (top10["records"] / total * 100).round(1) if total else 0.0
    top10 = top10.sort_values("records", ascending=True)
    top10["convenio"] = top10["convenio"].astype(str)

    fig = go.Figure(go.Bar(
        y=top10["convenio"],
        x=top10["records"],
        orientation="h",
        marker=dict(color="#1565C0"),
        text=top10["pct"].apply(lambda x: f"{x:.1f}%"),
        textposition="outside",
        hovertemplate="%{y}<br>Registros: %{x:,.0f}<br>%{customdata} del total<extra></extra>",
        customdata=top10["pct"],
    ))
    fig.update_layout(
        height=350,
        margin=dict(l=10, r=50, t=10, b=10),
        xaxis_title=None,
        yaxis_title=None,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#1A2A45", size=11),
        xaxis=dict(gridcolor="#EDF1F7", zerolinecolor="#EDF1F7"),
        showlegend=False,
        bargap=0.3,
    )
    fig.update_xaxes(tickformat=",.0f")
    _render_interactive_chart(fig, "conv_records_top10", view_key)


def plot_conv_valor_top10(df: pd.DataFrame, view_key=None):
    if df is None or df.empty:
        st.info("No hay datos de convenios por valor.")
        return

    active = get_viz_filter(view_key) if view_key else None
    chart_df = df.copy()
    if active and "convenio" in chart_df.columns:
        chart_df = chart_df[chart_df["convenio"].astype(str).str.strip().str.lower() == active.strip().lower()]
        if chart_df.empty:
            st.info(f"No hay datos para el filtro: {active}")
            return

    total = chart_df["valor"].sum()
    top10 = chart_df.nlargest(10, "valor").copy()
    top10["pct"] = (top10["valor"] / total * 100).round(1) if total else 0.0
    top10 = top10.sort_values("valor", ascending=True)
    top10["convenio"] = top10["convenio"].astype(str)

    fig = go.Figure(go.Bar(
        y=top10["convenio"],
        x=top10["valor"],
        orientation="h",
        marker=dict(color="#F57C00"),
        text=top10.apply(lambda r: f"{_fmt_compact(r['valor'])}  ·  {r['pct']:.1f}%", axis=1),
        textposition="outside",
        hovertemplate="%{y}<br>Valor: $%{x:,.0f}<br>%{customdata:.1f}% del total<extra></extra>",
        customdata=top10["pct"],
    ))
    fig.update_layout(
        height=350,
        margin=dict(l=10, r=180, t=10, b=10),
        xaxis_title=None,
        yaxis_title=None,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#1A2A45", size=11),
        xaxis=dict(gridcolor="#EDF1F7", zerolinecolor="#EDF1F7"),
        showlegend=False,
        bargap=0.3,
    )
    fig.update_xaxes(tickformat=",.0f")
    _render_interactive_chart(fig, "conv_valor_top10", view_key)
