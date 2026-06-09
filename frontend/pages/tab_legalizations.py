import pandas as pd
import streamlit as st

from frontend.services.legalizations_service import (
    LegalizationsService,
)

ALL_OPTION = "Todos"


def render_tab_legalizations():
    st.header("📋 Legalizaciones")

    start_date = st.session_state.get(
        "global_start_date"
    )

    end_date = st.session_state.get(
        "global_end_date"
    )

    selected_user = st.session_state.get(
        "global_user",
        ALL_OPTION,
    )

    selected_users = (
        None
        if selected_user == ALL_OPTION
        else [selected_user]
    )
    token = st.session_state.get("token")
    if not token:
        st.warning("Debes iniciar sesión para ver las legalizaciones.")
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

    tab_ppl, tab_agreements = st.tabs(
        [
            "📋 PPL",
            "📋 Convenios",
        ]
    )

    with tab_ppl:

        _render_productivity_section(
            metrics=metrics.ppl,
            title="Legalizaciones PPL",
        )

    with tab_agreements:

        _render_productivity_section(
            metrics=metrics.agreements,
            title="Legalizaciones Convenios",
        )


def _render_productivity_section(
        metrics,
        title: str,
):

    st.subheader(title)

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            label="Total registros",
            value=f"{metrics.total:,}",
        )

    with col2:

        st.metric(
            label="Promedio diario",
            value=round(
                metrics.daily_average,
                2,
            ),
        )

    st.divider()

    tab_users, tab_dates = st.tabs(
        [
            "👤 Por usuario",
            "📅 Por fecha",
        ]
    )

    with tab_users:

        user_df = pd.DataFrame(
            metrics.by_user
        )

        if user_df.empty:

            st.info(
                "No existen registros para los filtros seleccionados."
            )

        else:

            st.dataframe(
                user_df,
                use_container_width=True,
            )

            if (
                    "USUARIO" in user_df.columns
                    and "REGISTROS" in user_df.columns
            ):

                st.bar_chart(
                    data=user_df,
                    x="USUARIO",
                    y="REGISTROS",
                )

    with tab_dates:

        date_df = pd.DataFrame(
            metrics.by_date
        )

        if date_df.empty:

            st.info(
                "No existen registros para los filtros seleccionados."
            )

        else:

            st.dataframe(
                date_df,
                use_container_width=True,
            )

            if (
                    "DATE" in date_df.columns
                    and "REGISTROS" in date_df.columns
            ):

                st.line_chart(
                    data=date_df.set_index("DATE"),
                    y="REGISTROS",
                )
