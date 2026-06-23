"""
Admin Panel — User Management & Report Downloads
=================================================
- Solo accesible para rol ADMIN
- Gestión de usuarios (listar, editar, activar/desactivar)
- Descarga rápida de informes
"""

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from frontend.services.users_service import UsersFrontendService
from frontend.services.export_service import ExportFrontendService
from ui.goleman_theme import GolemanTheme


_ROLES = ["Facturador", "Auditor", "Administrativo", "Coordinador", "SUPERVISOR", "ADMIN"]


def _check_admin():
    user = st.session_state.get("user", {})
    if user.get("role") != "ADMIN":
        st.error("No tienes permisos para acceder al panel de administración.")
        st.stop()


def _render_users_management():
    st.markdown(GolemanTheme.section_header("Gestión de Usuarios", "Listar, editar y activar/desactivar usuarios"), unsafe_allow_html=True)

    token = st.session_state.get("token")
    service = UsersFrontendService(token=token)

    # Filters row
    col_search, col_role, col_page, col_refresh = st.columns([3, 2, 1, 1])
    with col_search:
        search = st.text_input("Buscar por nombre o email", key="admin_search", placeholder="Escribe para buscar...")
    with col_role:
        role_filter = st.selectbox("Filtrar por rol", ["Todos"] + _ROLES, key="admin_role_filter")
        if role_filter == "Todos":
            role_filter = None
    with col_page:
        page = st.number_input("Página", min_value=1, value=1, key="admin_page")
    with col_refresh:
        st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
        st.button("🔄", key="admin_refresh", use_container_width=True)

    try:
        result = service.list_users(page=page, size=20, search=search if search else None, role_filter=role_filter)
    except Exception as e:
        st.error(f"Error al cargar usuarios: {e}")
        return

    users = result.get("users", [])
    total = result.get("total", 0)

    if not users:
        st.info("No se encontraron usuarios.")
        return

    st.markdown(f"**{total} usuarios encontrados** | Página {page} de {max(1, (total + 19) // 20)}")

    # Build table
    rows = []
    for u in users:
        status = "🟢 Activo" if u.get("is_active", True) else "🔴 Inactivo"
        rows.append({
            "ID": u.get("id"),
            "Username": u.get("username", ""),
            "Email": u.get("email", ""),
            "Rol": u.get("role", "Sin rol"),
            "Estado": status,
        })

    df = pd.DataFrame(rows)

    # Display as styled table
    for i, u in enumerate(users):
        col_id, col_name, col_email, col_role, col_status, col_actions = st.columns([0.5, 2, 2.5, 1.5, 1, 1.5])
        with col_id:
            st.markdown(f"<div style='padding-top:8px;font-size:11px;color:{GolemanTheme.MUTED}'>{u.get('id')}</div>", unsafe_allow_html=True)
        with col_name:
            st.markdown(f"<div style='padding-top:8px;font-size:13px;color:{GolemanTheme.TEXT};font-weight:500'>{u.get('username', '')}</div>", unsafe_allow_html=True)
        with col_email:
            st.markdown(f"<div style='padding-top:8px;font-size:12px;color:{GolemanTheme.MUTED}'>{u.get('email', '')}</div>", unsafe_allow_html=True)
        with col_role:
            st.markdown(f"<div style='padding-top:8px;font-size:12px;color:{GolemanTheme.TEXT}'>{u.get('role', '')}</div>", unsafe_allow_html=True)
        with col_status:
            color = GolemanTheme.SUCCESS if u.get("is_active", True) else GolemanTheme.DANGER
            status = "Activo" if u.get("is_active", True) else "Inactivo"
            st.markdown(
                f"<span style='font-size:11px;padding:2px 8px;border-radius:10px;color:{color};background:{GolemanTheme.WHITE};border:0.5px solid {color}'>{status}</span>",
                unsafe_allow_html=True,
            )
        with col_actions:
            col_edit, col_toggle = st.columns(2)
            with col_edit:
                if st.button("✏️", key=f"edit_user_{u.get('id')}", help="Editar usuario"):
                    st.session_state[f"_editing_user_{u.get('id')}"] = True
            with col_toggle:
                btn_label = "🔴" if u.get("is_active", True) else "🟢"
                if st.button(btn_label, key=f"toggle_user_{u.get('id')}", help="Activar/Desactivar"):
                    try:
                        service.toggle_active(u.get("id"))
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

        # Edit form (shown when editing)
        if st.session_state.get(f"_editing_user_{u.get('id')}", False):
            with st.expander(f"Editar: {u.get('username', '')}", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    new_username = st.text_input("Username", value=u.get("username", ""), key=f"edit_username_{u.get('id')}")
                with col2:
                    new_email = st.text_input("Email", value=u.get("email", ""), key=f"edit_email_{u.get('id')}")
                with col3:
                    current_role = u.get("role", "")
                    role_index = _ROLES.index(current_role) if current_role in _ROLES else 0
                    new_role = st.selectbox("Rol", _ROLES, index=role_index, key=f"edit_role_{u.get('id')}")

                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("💾 Guardar", key=f"save_user_{u.get('id')}", type="primary", use_container_width=True):
                        try:
                            service.update_user(u.get("id"), {
                                "username": new_username,
                                "email": new_email,
                                "role": new_role,
                            })
                            st.session_state.pop(f"_editing_user_{u.get('id')}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al guardar: {e}")
                with col_cancel:
                    if st.button("Cancelar", key=f"cancel_edit_{u.get('id')}", use_container_width=True):
                        st.session_state.pop(f"_editing_user_{u.get('id')}")
                        st.rerun()

        st.markdown(f"<hr style='margin:4px 0;border:none;border-top:0.5px solid {GolemanTheme.BORDER};opacity:0.5'>", unsafe_allow_html=True)


def _render_reports_download():
    st.markdown(GolemanTheme.section_header("Descarga de Informes", "Exporta informes de cualquier módulo"), unsafe_allow_html=True)

    token = st.session_state.get("token")
    export_service = ExportFrontendService(token=token)
    users_service = UsersFrontendService(token=token)

    # --- User dropdown ---
    result = users_service.list_users(page=1, size=100)
    all_users = result.get("users", [])

    user_names = sorted([u.get("username", "") for u in all_users if u.get("username")])
    selected_users = st.multiselect(
        "Filtrar por usuario (vacío = todos)",
        options=user_names,
        key="admin_report_users",
    ) or None

    # --- Dates ---
    start_date = st.session_state.get("global_start_date", date.today() - timedelta(days=29))
    end_date = st.session_state.get("global_end_date", date.today())

    col1, col2 = st.columns(2)
    with col1:
        report_start = st.date_input("Fecha inicio", value=start_date, key="admin_report_start")
    with col2:
        report_end = st.date_input("Fecha fin", value=end_date, key="admin_report_end")

    st.markdown("---")

    reports = [
        ("general", "📊 Informe General", "Todos los módulos combinados"),
        ("billing", "💰 Facturación Electrónica", "KPIs, productividad, tendencias"),
        ("legalizations", "📋 Legalizaciones", "PPL y Convenios"),
        ("rips", "📄 RIPS", "Productividad de RIPS"),
        ("radicacion", "📬 Radicación", "Facturas vencidas y SLA"),
        ("processes", "⚙️ Procesos Administrativos", "Registros por persona y proceso"),
    ]

    for key, label, desc in reports:
        col_btn, col_desc = st.columns([1, 3])
        with col_btn:
            if st.button(label, key=f"admin_export_{key}", use_container_width=True, type="primary" if key == "general" else "secondary"):
                with st.spinner(f"Generando {label}..."):
                    try:
                        file_bytes, filename = export_service.export_module(key, report_start, report_end, selected_users)
                        st.session_state[f"_admin_file_{key}"] = file_bytes
                        st.session_state[f"_admin_filename_{key}"] = filename
                    except Exception as e:
                        st.error(f"Error al generar {label}: {e}")

        with col_desc:
            st.markdown(f"<div style='padding-top:4px;font-size:12px;color:{GolemanTheme.MUTED}'>{desc}</div>", unsafe_allow_html=True)

        # Download button
        file_bytes = st.session_state.get(f"_admin_file_{key}")
        filename = st.session_state.get(f"_admin_filename_{key}")
        if file_bytes and filename:
            st.download_button(
                label="⬇️ Descargar",
                data=file_bytes,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"admin_download_{key}",
                use_container_width=True,
            )


def render_admin_panel():
    _check_admin()

    st.markdown(f"""
    <div style="
        background:{GolemanTheme.NAVY};
        border-radius:14px;
        padding:20px 28px;
        margin-bottom:18px;
    ">
      <div style="font-size:11px;color:rgba(255,255,255,.4);
                  letter-spacing:.06em;text-transform:uppercase;
                  margin-bottom:5px">Panel de Administración</div>
      <div style="font-size:20px;font-weight:600;color:#fff;margin-bottom:3px">
        Administración del Sistema
      </div>
      <div style="font-size:12px;color:rgba(255,255,255,.4)">
        Gestión de usuarios y descarga de informes
      </div>
    </div>
    """, unsafe_allow_html=True)

    tab_users, tab_reports = st.tabs(["👥 Gestión de Usuarios", "📥 Descarga de Informes"])

    with tab_users:
        _render_users_management()

    with tab_reports:
        _render_reports_download()
