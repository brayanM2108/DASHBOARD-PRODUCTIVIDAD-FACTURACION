import pandas as pd
import streamlit as st

from frontend.services.rips_service import RipsFrontendService

ALL_OPTION = "Todos"


def render_tab_rips():
    st.header("📄 RIPS")

    start_date = st.session_state.get("global_start_date")
    end_date = st.session_state.get("global_end_date")
    selected_user = st.session_state.get("global_user", ALL_OPTION)

    selected_users = (
        None if selected_user == ALL_OPTION else [selected_user]
    )

    token = st.session_state.get("token")
    if not token:
        st.warning("Debes iniciar sesión para ver los RIPS.")
        return

    service = RipsFrontendService()
    result = service.get_metrics(
        start_date=start_date,
        end_date=end_date,
        selected_users=selected_users,
    )

    if result.error:
        st.error(result.error)
        return

    metrics = result.metrics
    _render_kpis(metrics)
    _render_charts_and_tables(metrics)


def _render_kpis(metrics):
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total registros", value=f"{metrics.total:,}")
    with col2:
        st.metric(label="Promedio diario", value=round(metrics.daily_average, 2))

    st.divider()


def _render_charts_and_tables(metrics):
    tab_users, tab_dates = st.tabs(["👤 Por usuario", "📅 Por fecha"])

    with tab_users:
        user_df = pd.DataFrame(metrics.by_user)
        if user_df.empty:
            st.info("No existen registros para los filtros seleccionados.")
        else:
            st.dataframe(user_df, use_container_width=True)
            col_label = [c for c in user_df.columns if c != "REGISTROS"][0]
            if col_label and "REGISTROS" in user_df.columns:
                st.bar_chart(data=user_df, x=col_label, y="REGISTROS")

    with tab_dates:
        date_df = pd.DataFrame(metrics.by_date)
        if date_df.empty:
            st.info("No existen registros para los filtros seleccionados.")
        else:
            st.dataframe(date_df, use_container_width=True)
            if "DATE" in date_df.columns and "REGISTROS" in date_df.columns:
                st.line_chart(data=date_df.set_index("DATE"), y="REGISTROS")
