"""
Export Panel — Reusable export component for all views.
=======================================================
Provides a button that opens an expander with date/user filters
and a download button for the Excel report.
"""

from datetime import date, timedelta

import streamlit as st

from frontend.services.export_service import ExportFrontendService
from ui.goleman_theme import GolemanTheme


_MODULE_LABELS = {
    "general": "Informe General",
    "billing": "Facturación Electrónica",
    "legalizations": "Legalizaciones",
    "rips": "RIPS",
    "radicacion": "Radicación",
    "processes": "Procesos Administrativos",
}


def render_export_section(
    module: str,
    start_date: date | None = None,
    end_date: date | None = None,
    allow_user_filter: bool = False,
) -> None:
    """
    Render export button + expander with filters + download button.

    Args:
        module: One of 'general', 'billing', 'legalizations', 'rips', 'radicacion', 'processes'
        start_date: Default start date (defaults to 30 days ago)
        end_date: Default end date (defaults to today)
        allow_user_filter: If True, show user selector (admin only)
    """
    label = _MODULE_LABELS.get(module, module)
    token = st.session_state.get("token")
    user = st.session_state.get("user", {})
    role = user.get("role", "")
    is_admin = role in ("ADMIN", "SUPERVISOR")

    if start_date is None:
        start_date = date.today() - timedelta(days=29)
    if end_date is None:
        end_date = date.today()

    # Use global filter dates if available
    global_start = st.session_state.get("global_start_date")
    global_end = st.session_state.get("global_end_date")
    if global_start and isinstance(global_start, date):
        start_date = global_start
    if global_end and isinstance(global_end, date):
        end_date = global_end

    # Export button
    if st.button(f"📥 Exportar {label}", key=f"btn_export_{module}", use_container_width=True):
        st.session_state[f"_show_export_{module}"] = not st.session_state.get(f"_show_export_{module}", False)
        st.rerun()

    # Expander with filters and download
    if st.session_state.get(f"_show_export_{module}", False):
        with st.expander("Configurar y descargar informe", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                exp_start = st.date_input(
                    "Fecha inicio",
                    value=start_date,
                    key=f"exp_start_{module}",
                )
            with col2:
                exp_end = st.date_input(
                    "Fecha fin",
                    value=end_date,
                    key=f"exp_end_{module}",
                )

            selected_users = None
            if allow_user_filter and is_admin:
                global_user = st.session_state.get("global_user")
                user_options = ["Todos"]
                billers_df = st.session_state.get("billers_df")
                if billers_df is not None and not billers_df.empty:
                    name_col = None
                    for col in ["NOMBRE", "nombre", "USUARIO", "usuario"]:
                        if col in billers_df.columns:
                            name_col = col
                            break
                    if name_col:
                        user_options = ["Todos"] + sorted(billers_df[name_col].dropna().unique().tolist())

                selected_user = st.selectbox(
                    "Filtrar por usuario",
                    options=user_options,
                    index=0,
                    key=f"exp_user_{module}",
                )
                if selected_user and selected_user != "Todos":
                    selected_users = [selected_user]

            if st.button("📄 Generar informe", key=f"btn_generate_{module}", type="primary", use_container_width=True):
                with st.spinner("Generando informe..."):
                    try:
                        service = ExportFrontendService(token=token)
                        file_bytes, filename = service.export_module(
                            module, exp_start, exp_end, selected_users
                        )
                        st.session_state[f"_export_bytes_{module}"] = file_bytes
                        st.session_state[f"_export_filename_{module}"] = filename
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al generar informe: {e}")

            # Download button (shown after generation)
            file_bytes = st.session_state.get(f"_export_bytes_{module}")
            filename = st.session_state.get(f"_export_filename_{module}")
            if file_bytes and filename:
                st.download_button(
                    label="⬇️ Descargar Excel",
                    data=file_bytes,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"download_{module}",
                    use_container_width=True,
                )
