"""
Billing tab
===========
UI to visualize and analyze electronic billing productivity.
Uses 3 endpoints: /summary, /analytics, /detail.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from frontend.components.components import show_info_message
from frontend.components.visualizations import (
    plot_billing_records_by_user,
    plot_billing_records_trend,
    plot_billing_trend,
    plot_billing_value_by_user,
    plot_conv_records_top10,
    plot_conv_valor_top10,
    clear_viz_filter,
    any_viz_filter_active,
)
from frontend.services.billing_service import ElectronicBillingFrontendService
from frontend.exceptions import ApiException
from ui.goleman_theme import GolemanTheme


_VIZ_KEY = "billing"


def _format_compact_money(value: float) -> str:
    return f"${value:,.2f}"


def _section_title(label: str) -> None:
    st.markdown(f'<div class="g-section-title">{label}</div>', unsafe_allow_html=True)


def _insight_html(item) -> str:
    colors = {
        "success": (GolemanTheme.SUCCESS_LIGHT, GolemanTheme.SUCCESS),
        "info": (GolemanTheme.BG, GolemanTheme.BLUE),
        "warning": (GolemanTheme.WARNING_LIGHT, GolemanTheme.ORANGE),
    }
    bg, accent = colors.get(item.type, colors["info"])
    return (
        f'<div style="background:{bg};border-left:3px solid {accent};'
        f'border-radius:8px;padding:12px 16px;margin-bottom:8px">'
        f'<div style="font-size:11px;font-weight:600;color:{accent};'
        f'text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">'
        f'{item.title}</div>'
        f'<div style="font-size:12px;color:{GolemanTheme.TEXT}">{item.description}</div>'
        f'</div>'
    )


def render_tab_billing_electronic():
    render_billing_electronic_section()


def render_billing_electronic_section():
    e_billing_df = st.session_state.get("electronic_billing_df")

    if e_billing_df is None or e_billing_df.empty:
        show_info_message("No hay datos de facturacion electronica. Carga un archivo en la seccion de carga.")
        return

    st.markdown(
        """
        <div class="g-tab-header">
          <div class="g-tab-header-title"><span>▣</span>Productividad · Facturacion electronica</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    start_date = st.session_state.get("global_start_date")
    end_date = st.session_state.get("global_end_date")
    selected_user = st.session_state.get("global_user")

    user = st.session_state.get("user", {})
    role = user.get("role") if user else None
    if role in ("ADMIN", "SUPERVISOR"):
        selected_users = [selected_user] if selected_user and selected_user != "Todos" else None
    else:
        selected_users = None
    selected_agreement = None

    token = st.session_state.get("token")
    if not token:
        show_info_message("Debes iniciar sesion para ver la facturacion.")
        return

    service = ElectronicBillingFrontendService(token=token)

    try:
        summary = service.get_summary(
            start_date=start_date,
            end_date=end_date,
            selected_users=selected_users,
            selected_agreement=selected_agreement,
        )
    except ApiException as e:
        st.warning(str(e))
        return

    kpis = summary.kpis
    period = summary.period

    _section_title("Metricas del periodo")
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Total registros", f"{kpis.total_records:,}")
    with k2:
        st.metric("Valor facturado", _format_compact_money(kpis.total_valor_tercero))
    with k3:
        st.metric("Prom. diario registros", f"{kpis.daily_avg_records:,.0f}")
    with k4:
        st.metric("Ticket promedio", _format_compact_money(kpis.average_ticket))

    if period and period.last_update:
        st.caption(f"Ultima actualizacion: {period.last_update[:19].replace('T', ' ')}")

    if any_viz_filter_active(_VIZ_KEY):
        if st.button("Limpiar filtro", key="clear_bill_filter", use_container_width=True):
            clear_viz_filter(_VIZ_KEY)
            st.rerun()

    tab_graficos, tab_detalle = st.tabs(["Graficos y Analytics", "Tabla de detalle"])

    with tab_graficos:
        try:
            analytics = service.get_analytics(
                start_date=start_date,
                end_date=end_date,
                selected_users=selected_users,
                selected_agreement=selected_agreement,
            )
        except ApiException as e:
            st.warning(str(e))
            analytics = None

        if analytics:
            df_by_user = pd.DataFrame([u.__dict__ for u in analytics.user_distribution])
            df_by_date = pd.DataFrame([d.__dict__ for d in analytics.daily_trend])

            df_chart_users = df_by_user.rename(columns={
                "usuario": "USUARIO", "records": "REGISTROS", "valor": "VALOR_TERCERO",
            }) if not df_by_user.empty else df_by_user
            df_chart_dates = df_by_date.rename(columns={
                "date": "DATE", "records": "REGISTROS", "valor": "VALOR_TERCERO",
            }) if not df_by_date.empty else df_by_date

            result_user_col = "USUARIO" if "USUARIO" in (df_chart_users.columns if not df_chart_users.empty else []) else (
                df_chart_users.columns[0] if not df_chart_users.empty else "USUARIO"
            )

            sub_tab_users, sub_tab_dates, sub_tab_eps, sub_tab_convenios, sub_tab_insights = st.tabs(
                ["Por usuario", "Tendencia diaria", "EPS", "Convenios", "Insights"]
            )

            with sub_tab_users:
                if not df_by_user.empty:

                    _section_title("Registros por usuario")
                    plot_billing_records_by_user(df_chart_users, result_user_col, view_key=_VIZ_KEY)

                    _section_title("Valor facturado por usuario")
                    plot_billing_value_by_user(df_chart_users, result_user_col, view_key=_VIZ_KEY)

                    display_df = df_by_user.copy()
                    display_df["VALOR TERCERO"] = display_df["valor"].map(lambda v: f"${v:,.0f}")
                    st.dataframe(
                        display_df[["usuario", "records", "VALOR TERCERO", "ticket_promedio", "participacion_records", "participacion_valor"]],
                        width="stretch",
                        hide_index=True,
                        column_config={
                            "usuario": "Usuario",
                            "records": st.column_config.NumberColumn("Registros", format="%d"),
                            "VALOR TERCERO": "Valor facturado",
                            "ticket_promedio": st.column_config.NumberColumn("Ticket prom.", format="$%.0f"),
                            "participacion_records": st.column_config.NumberColumn("% Registros", format="%.1f%%"),
                            "participacion_valor": st.column_config.NumberColumn("% Valor", format="%.1f%%"),
                        },
                    )

            with sub_tab_dates:
                col_reg, col_val = st.columns(2)
                with col_reg:
                    _section_title("Registros por fecha")
                    plot_billing_records_trend(df_chart_dates, view_key=_VIZ_KEY)
                with col_val:
                    _section_title("Valor facturado acumulado")
                    plot_billing_trend(df_chart_dates, view_key=_VIZ_KEY)

            with sub_tab_eps:
                df_eps = pd.DataFrame([e.__dict__ for e in analytics.eps_distribution])

                if df_eps.empty:
                    show_info_message("No hay datos de EPS.")
                else:
                    col_eps_rec, col_eps_val = st.columns(2)
                    with col_eps_rec:
                        _section_title("Registros por EPS")
                        fig_eps_rec = px.pie(
                            df_eps, names="eps", values="records", hole=0.55,
                            color_discrete_sequence=[GolemanTheme.BLUE, GolemanTheme.ORANGE, GolemanTheme.SUCCESS,
                                                      GolemanTheme.NAVY2, GolemanTheme.WARNING,
                                                      GolemanTheme.SKY, GolemanTheme.DANGER, GolemanTheme.BLUE_LIGHT,
                                                      GolemanTheme.NAVY, GolemanTheme.ORANGE_LIGHT],
                        )
                        fig_eps_rec.update_traces(
                            textposition="inside", textinfo="percent",
                            hovertemplate="%{label}<br>%{value:,} registros<extra></extra>",
                        )
                        fig_eps_rec.update_layout(
                            height=300, margin=dict(l=0, r=0, t=0, b=0),
                            paper_bgcolor=GolemanTheme.WHITE, font=dict(color=GolemanTheme.TEXT, size=11),
                            showlegend=True, legend=dict(orientation="h", y=-0.1,
                                                         font=dict(size=10, color=GolemanTheme.MUTED)),
                        )
                        st.plotly_chart(fig_eps_rec, use_container_width=True, config={"displayModeBar": False})
                    with col_eps_val:
                        _section_title("Valor por EPS")
                        fig_eps_val = px.pie(
                            df_eps, names="eps", values="valor", hole=0.55,
                            color_discrete_sequence=[GolemanTheme.BLUE, GolemanTheme.ORANGE, GolemanTheme.SUCCESS,
                                                      GolemanTheme.NAVY2, GolemanTheme.WARNING,
                                                      GolemanTheme.SKY, GolemanTheme.DANGER, GolemanTheme.BLUE_LIGHT,
                                                      GolemanTheme.NAVY, GolemanTheme.ORANGE_LIGHT],
                        )
                        fig_eps_val.update_traces(
                            textposition="inside", textinfo="percent",
                            hovertemplate="%{label}<br>$%{value:,.0f}<extra></extra>",
                        )
                        fig_eps_val.update_layout(
                            height=300, margin=dict(l=0, r=0, t=0, b=0),
                            paper_bgcolor=GolemanTheme.WHITE, font=dict(color=GolemanTheme.TEXT, size=11),
                            showlegend=True, legend=dict(orientation="h", y=-0.1,
                                                         font=dict(size=10, color=GolemanTheme.MUTED)),
                        )
                        st.plotly_chart(fig_eps_val, use_container_width=True, config={"displayModeBar": False})

                    st.dataframe(
                        df_eps,
                        width="stretch",
                        hide_index=True,
                        column_config={
                            "eps": "EPS",
                            "records": st.column_config.NumberColumn("Registros", format="%d"),
                            "valor": st.column_config.NumberColumn("Valor", format="$%.0f"),
                        },
                    )

            with sub_tab_convenios:
                df_conv = pd.DataFrame([c.__dict__ for c in analytics.convenio_distribution])

                if df_conv.empty:
                    show_info_message("No hay datos de convenios.")
                else:
                    col_conv_rec, col_conv_val = st.columns(2)
                    with col_conv_rec:
                        _section_title("Top 10 Convenios · Registros")
                        plot_conv_records_top10(df_conv, view_key=_VIZ_KEY)
                    with col_conv_val:
                        _section_title("Top 10 Convenios · Valor")
                        plot_conv_valor_top10(df_conv, view_key=_VIZ_KEY)

                    st.dataframe(
                        df_conv,
                        width="stretch",
                        hide_index=True,
                        column_config={
                            "convenio": "Convenio",
                            "records": st.column_config.NumberColumn("Registros", format="%d"),
                            "valor": st.column_config.NumberColumn("Valor", format="$%.0f"),
                        },
                    )

            with sub_tab_insights:
                _section_title("Insights del periodo")
                for ins in analytics.insights:
                    st.markdown(_insight_html(ins), unsafe_allow_html=True)

                rankings = analytics.rankings
                if rankings.top_records or rankings.top_valor:
                    _section_title("Rankings")
                    cr, cv = st.columns(2)
                    with cr:
                        st.markdown(
                            f'<div style="font-size:12px;font-weight:600;color:{GolemanTheme.NAVY};margin-bottom:4px">'
                            f'Top registros</div>',
                            unsafe_allow_html=True,
                        )
                        for i, r in enumerate(rankings.top_records, 1):
                            st.markdown(
                                f'<div style="font-size:12px;padding:3px 0">{i}. {r.usuario} — {r.records:,}</div>',
                                unsafe_allow_html=True,
                            )
                    with cv:
                        st.markdown(
                            f'<div style="font-size:12px;font-weight:600;color:{GolemanTheme.NAVY};margin-bottom:4px">'
                            f'Top valor</div>',
                            unsafe_allow_html=True,
                        )
                        for i, v in enumerate(rankings.top_valor, 1):
                            st.markdown(
                                f'<div style="font-size:12px;padding:3px 0">{i}. {v.usuario} — ${v.valor:,.0f}</div>',
                                unsafe_allow_html=True,
                            )

    with tab_detalle:
        detail_page = st.session_state.get("_bill_detail_page", 1)

        try:
            detail = service.get_detail(
                start_date=start_date,
                end_date=end_date,
                selected_users=selected_users,
                selected_agreement=selected_agreement,
                page=detail_page,
                page_size=50,
            )
        except ApiException as e:
            st.warning(str(e))
            detail = None

        if detail:
            pag = detail.pagination
            total_pages = max(1, (pag.total + pag.page_size - 1) // pag.page_size)

            st.caption(f"Mostrando {len(detail.data)} de {pag.total:,} registros · Pagina {pag.page} de {total_pages}")

            cp1, cp2, cp3, cp4, cp5 = st.columns([1, 1, 1, 1, 3])
            with cp1:
                if st.button("◀ Anterior", disabled=(detail_page <= 1), use_container_width=True, key="bill_prev"):
                    st.session_state["_bill_detail_page"] = max(1, detail_page - 1)
                    st.rerun()
            with cp2:
                if st.button("Siguiente ▶", disabled=(detail_page >= total_pages), use_container_width=True, key="bill_next"):
                    st.session_state["_bill_detail_page"] = min(total_pages, detail_page + 1)
                    st.rerun()
            with cp3:
                go_page = st.number_input("Ir a pagina", min_value=1, max_value=total_pages, value=detail_page, key="bill_goto")
            with cp4:
                if st.button("Ir", use_container_width=True, key="bill_go"):
                    st.session_state["_bill_detail_page"] = go_page
                    st.rerun()

            df_detail = pd.DataFrame([d.__dict__ for d in detail.data])
            if not df_detail.empty:
                st.dataframe(
                    df_detail,
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "identificacion": "ID",
                        "factura": "Factura",
                        "usuario": "Usuario",
                        "eps": "EPS",
                        "convenio": "Convenio",
                        "fecha_factura": "Fecha factura",
                        "fecha_legalizacion": "Fecha legalizacion",
                        "paciente": "Paciente",
                        "valor_tercero": st.column_config.NumberColumn("Valor tercero", format="$%.0f"),
                        "estado": "Estado",
                    },
                )
            else:
                show_info_message("No hay registros en esta pagina.")


