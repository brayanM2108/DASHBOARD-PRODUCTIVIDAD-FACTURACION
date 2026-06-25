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
from frontend.services.auth_service import AuthFrontendService
from frontend.services.process_config_service import ProcessConfigFrontendService
from frontend.api.billers_admin_api import BillersAdminApi
from ui.goleman_theme import GolemanTheme


_ROLES = ["Facturador", "Auditor", "Administrativo", "Coordinador", "SUPERVISOR", "ADMIN"]


def _check_admin():
    user = st.session_state.get("user", {})
    if user.get("role") != "ADMIN":
        st.error("No tienes permisos para acceder al panel de administración.")
        st.stop()


_ROLE_BADGE_STYLES = {
    "ADMIN":        ("#FDECEC", "#D32F2F"),
    "SUPERVISOR":   ("#E8F0FE", "#1A56DB"),
    "Coordinador":  ("#E6F4EA", "#1E8E3E"),
    "Facturador":   ("#EBF4FF", "#1565C0"),
    "Auditor":      ("#F3E8FF", "#7C3AED"),
    "Administrativo": ("#F1F5F9", "#475569"),
}
_DEFAULT_ROLE_BG, _DEFAULT_ROLE_FG = "#F1F5F9", "#5A6A84"


def _user_initials(username: str) -> str:
    parts = username.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return username[:2].upper() if username else "?"


def _avatar_html(initials: str, color: str = "#f97838") -> str:
    return (
        f"<div style='width:36px;height:36px;border-radius:10px;"
        f"background:rgba(249,120,56,.10);color:{color};"
        f"display:flex;align-items:center;justify-content:center;"
        f"font-size:13px;font-weight:700;flex-shrink:0'>"
        f"{initials}</div>"
    )


def _role_badge(role: str) -> str:
    bg, fg = _ROLE_BADGE_STYLES.get(role, (_DEFAULT_ROLE_BG, _DEFAULT_ROLE_FG))
    return (
        f"<span style='display:inline-block;border-radius:999px;"
        f"padding:4px 12px;font-size:11px;font-weight:500;"
        f"background:{bg};color:{fg};white-space:nowrap'>{role or 'Sin rol'}</span>"
    )


def _status_pill(is_active: bool) -> str:
    if is_active:
        return (
            f"<span style='display:inline-flex;align-items:center;gap:6px;"
            f"padding:4px 12px;border-radius:999px;font-size:11px;font-weight:500;"
            f"background:#EAF8EF;color:#1E8E3E'>"
            f"<span style='width:6px;height:6px;border-radius:50%;background:#1E8E3E'></span>"
            f"Activo</span>"
        )
    return (
        f"<span style='display:inline-flex;align-items:center;gap:6px;"
        f"padding:4px 12px;border-radius:999px;font-size:11px;font-weight:500;"
        f"background:#FFF4E5;color:#F57C00'>"
        f"<span style='width:6px;height:6px;border-radius:50%;background:#F57C00'></span>"
        f"Inactivo</span>"
    )


def _render_users_management():
    token = st.session_state.get("token")
    service = UsersFrontendService(token=token)

    # --- Hero header card ---
    st.markdown(f"""
    <div style="background:{GolemanTheme.WHITE};border-radius:16px;padding:20px 28px;
                margin-bottom:18px;box-shadow:0 4px 20px rgba(0,0,0,.05);
                display:flex;align-items:center;gap:16px">
      <div style="width:48px;height:48px;border-radius:12px;
                  background:{GolemanTheme.ORANGE_LIGHT};color:{GolemanTheme.ORANGE};
                  display:flex;align-items:center;justify-content:center;
                  font-size:22px;flex-shrink:0">👥</div>
      <div>
        <div style="font-size:17px;font-weight:600;color:{GolemanTheme.TEXT}">Gestión de Usuarios</div>
        <div style="font-size:12px;color:{GolemanTheme.MUTED};margin-top:2px">Lista, edita y administra usuarios del sistema</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Global cards CSS ---
    st.markdown(f"""
    <style>
    .st-key-admin_users_filters_card,
    [data-st-key="admin_users_filters_card"] {{
        background:{GolemanTheme.WHITE} !important;
        border-radius:16px !important;
        padding:16px 20px !important;
        margin-bottom:14px !important;
        box-shadow:0 4px 20px rgba(0,0,0,.05) !important;
    }}
    .st-key-admin_users_filters_card button,
    [data-st-key="admin_users_filters_card"] button {{
        border-radius:10px !important;height:38px !important;
        padding:0 14px !important;font-size:13px !important;
    }}

    .st-key-admin_users_table_card,
    [data-st-key="admin_users_table_card"] {{
        background:{GolemanTheme.WHITE} !important;
        border-radius:16px !important;
        padding:16px 20px !important;
        box-shadow:0 4px 20px rgba(0,0,0,.05) !important;
    }}

    .admin-user-edit-panel {{
        background:{GolemanTheme.BG2};
        border-radius:10px;
        padding:16px 20px;
        margin-bottom:10px;
        border:0.5px solid {GolemanTheme.BORDER};
    }}
    .admin-user-edit-panel button {{
        border-radius:10px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # --- Filter bar card ---
    with st.container(key="admin_users_filters_card"):
        col_search, col_role, col_page, col_refresh = st.columns([3, 2, 1, 1])
        with col_search:
            search = st.text_input(
                "Buscar por nombre o email", placeholder="Escribe para buscar...",
                key="admin_search",
            )
        with col_role:
            role_filter = st.selectbox(
                "Filtrar por rol", ["Todos"] + _ROLES, key="admin_role_filter",
            )
            if role_filter == "Todos":
                role_filter = None
        with col_page:
            page = st.number_input("Página", min_value=1, value=1, key="admin_page")
        with col_refresh:
            st.button("🔄 Refrescar", key="admin_refresh", use_container_width=True)

    # --- Fetch data ---
    try:
        result = service.list_users(page=page, size=20, search=search if search else None, role_filter=role_filter)
    except Exception as e:
        st.error(f"Error al cargar usuarios: {e}")
        return

    users = result.get("users", [])
    total = result.get("total", 0)
    total_pages = max(1, (total + 19) // 20)

    # --- Users card ---
    with st.container(key="admin_users_table_card"):
        st.markdown(
            f"<div style='font-size:12px;color:{GolemanTheme.MUTED};margin-bottom:12px'>"
            f"{total} usuarios encontrados</div>",
            unsafe_allow_html=True,
        )

        if not users:
            st.info("No se encontraron usuarios que coincidan con los filtros.")
            return

        for i, u in enumerate(users):
            user_id = u.get("id")
            username = u.get("username", "")
            email = u.get("email", "")
            role = u.get("role", "") or "Sin rol"
            is_active = u.get("is_active", True)
            initials = _user_initials(username)

            with st.container(key=f"user_row_{user_id}"):
                col_avatar, col_info, col_role, col_status, col_edit, col_reset, col_toggle = st.columns([0.6, 4, 1.4, 1.4, 0.6, 0.6, 0.6])
                with col_avatar:
                    st.markdown(_avatar_html(initials), unsafe_allow_html=True)
                with col_info:
                    st.markdown(
                        f"<div style='padding-top:2px'>"
                        f"<div style='font-size:13px;font-weight:500;color:{GolemanTheme.TEXT}'>{username}</div>"
                        f"<div style='font-size:11px;color:{GolemanTheme.MUTED};margin-top:1px'>{email}</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                with col_role:
                    st.markdown(f"<div style='padding-top:5px'>{_role_badge(role)}</div>", unsafe_allow_html=True)
                with col_status:
                    st.markdown(f"<div style='padding-top:5px'>{_status_pill(is_active)}</div>", unsafe_allow_html=True)
                with col_edit:
                    if st.button("✏️", key=f"edit_user_{user_id}", help="Editar usuario"):
                        st.session_state[f"_editing_user_{user_id}"] = True
                        st.rerun()
                with col_reset:
                    if st.button("🔑", key=f"reset_pw_{user_id}", help="Resetear contraseña"):
                        st.session_state[f"_resetting_pw_{user_id}"] = True
                        st.rerun()
                with col_toggle:
                    btn_icon = "🔴" if is_active else "🟢"
                    btn_help = "Desactivar usuario" if is_active else "Activar usuario"
                    if st.button(btn_icon, key=f"toggle_user_{user_id}", help=btn_help):
                        try:
                            service.toggle_active(user_id)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

            if st.session_state.get(f"_editing_user_{user_id}", False):
                st.markdown('<div class="admin-user-edit-panel">', unsafe_allow_html=True)
                st.markdown(
                    f"<div style='font-size:13px;font-weight:600;color:{GolemanTheme.TEXT};margin-bottom:12px'>"
                    f"Editando: {username}</div>",
                    unsafe_allow_html=True,
                )
                col1, col2, col3 = st.columns(3)
                with col1:
                    new_username = st.text_input("Username", value=username, key=f"edit_username_{user_id}")
                with col2:
                    new_email = st.text_input("Email", value=email, key=f"edit_email_{user_id}")
                with col3:
                    current_role = u.get("role", "")
                    role_index = _ROLES.index(current_role) if current_role in _ROLES else 0
                    new_role = st.selectbox("Rol", _ROLES, index=role_index, key=f"edit_role_{user_id}")

                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("💾 Guardar", key=f"save_user_{user_id}", type="primary", use_container_width=True):
                        try:
                            service.update_user(user_id, {
                                "username": new_username,
                                "email": new_email,
                                "role": new_role,
                            })
                            st.session_state.pop(f"_editing_user_{user_id}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al guardar: {e}")
                with col_cancel:
                    if st.button("Cancelar", key=f"cancel_edit_{user_id}", use_container_width=True):
                        st.session_state.pop(f"_editing_user_{user_id}")
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            if st.session_state.get(f"_resetting_pw_{user_id}", False):
                st.markdown('<div class="admin-user-edit-panel">', unsafe_allow_html=True)
                st.markdown(
                    f"<div style='font-size:13px;font-weight:600;color:{GolemanTheme.TEXT};margin-bottom:12px'>"
                    f"Resetear contraseña: {username}</div>",
                    unsafe_allow_html=True,
                )
                col_pw1, col_pw2 = st.columns([2, 1])
                with col_pw1:
                    new_pw = st.text_input(
                        "Nueva contraseña (vacío = generar aleatoria)",
                        key=f"new_pw_{user_id}",
                        placeholder="Dejar vacío para generar automática",
                    )
                with col_pw2:
                    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
                    if st.button("Resetear", key=f"do_reset_pw_{user_id}", type="primary", use_container_width=True):
                        try:
                            result = AuthFrontendService().admin_reset_password(
                                user_id, new_pw if new_pw else None
                            )
                            st.success(f"Contraseña: `{result.get('temp_password')}`")
                            st.info("Copia la contraseña y compártela con el usuario. Deberá cambiarla en su primer inicio de sesión.")
                        except Exception as e:
                            st.error(f"Error: {e}")

                if st.button("Cancelar", key=f"cancel_reset_pw_{user_id}", use_container_width=True):
                    st.session_state.pop(f"_resetting_pw_{user_id}")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        if total_pages > 1:
            st.markdown(f"""
            <div style="display:flex;justify-content:center;align-items:center;gap:8px;margin-top:16px">
              <span style="font-size:12px;color:{GolemanTheme.MUTED}">Página {page} de {total_pages}</span>
            </div>
            """, unsafe_allow_html=True)
            col_prev, col_page_input, col_next = st.columns([1, 1, 1])
            with col_prev:
                if st.button("◀ Anterior", disabled=page <= 1, key="admin_prev_page", use_container_width=True):
                    st.session_state["admin_page"] = page - 1
                    st.rerun()
            with col_page_input:
                go_page = st.number_input(
                    "Ir a", min_value=1, max_value=total_pages, value=page,
                    key="admin_go_page", label_visibility="collapsed",
                )
                if go_page != page:
                    st.session_state["admin_page"] = go_page
                    st.rerun()
            with col_next:
                if st.button("Siguiente ▶", disabled=page >= total_pages, key="admin_next_page", use_container_width=True):
                    st.session_state["admin_page"] = page + 1
                    st.rerun()


def _render_reports_download():
    st.markdown(GolemanTheme.section_header("Descarga de Informes", "Exporta informes de cualquier módulo"), unsafe_allow_html=True)

    from frontend.components.filters import render_role_user_filter

    token = st.session_state.get("token")
    export_service = ExportFrontendService(token=token)

    # --- Filter bar (same style as global filters) ---
    with st.container(key="admin_report_filters"):
        col_user, col_start, col_end = st.columns([3, 2, 2])

        with col_user:
            billers_df = st.session_state.get("billers_df")
            selected_user = render_role_user_filter(billers_df, key_prefix="admin_rpt")
            selected_users = None if selected_user == ["Todos"] else selected_user

        with col_start:
            report_start = st.date_input(
                "Fecha inicio",
                value=st.session_state.get("global_start_date", date.today() - timedelta(days=29)),
                key="admin_report_start",
            )

        with col_end:
            report_end = st.date_input(
                "Fecha fin",
                value=st.session_state.get("global_end_date", date.today()),
                key="admin_report_end",
            )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Inline CSS for cards
    st.markdown(f"""<style>
    [data-st-key^="report_card_"] {{
        background: {GolemanTheme.WHITE} !important;
        border: 0.5px solid {GolemanTheme.BORDER} !important;
        border-left: 3px solid {GolemanTheme.BLUE} !important;
        border-radius: 10px !important;
        padding: 8px 12px !important;
        margin-bottom: 10px !important;
        box-shadow: 0 1px 4px rgba(0,9,39,.04) !important;
    }}
    [data-st-key^="report_card_"] .stButton button,
    [data-st-key^="report_card_"] .stDownloadButton button {{
        font-size: 11px !important;
        padding: 2px 8px !important;
        height: 26px !important;
        min-height: 26px !important;
        line-height: 1 !important;
    }}
    [data-st-key^="report_card_"] [data-testid="stHorizontalBlock"] > div:nth-child(2),
    [data-st-key^="report_card_"] [data-testid="stHorizontalBlock"] > div:nth-child(3) {{
        display: flex !important;
        align-items: center !important;
    }}
    </style>""", unsafe_allow_html=True)

    # --- Report cards in 2 columns ---
    reports = [
        ("general", "📊 Informe General", "Todos los módulos"),
        ("billing", "💰 Facturación Electrónica", "KPIs y tendencias"),
        ("legalizations", "📋 Legalizaciones", "PPL y Convenios"),
        ("rips", "📄 RIPS", "Productividad RIPS"),
        ("radicacion", "📬 Radicación", "SLA y vencidas"),
        ("processes", "⚙️ Procesos Admin.", "Por persona/proceso"),
    ]

    col_a, col_b = st.columns(2)
    for i, (key, label, desc) in enumerate(reports):
        with (col_a if i % 2 == 0 else col_b):
            with st.container(key=f"report_card_{key}"):
                c_label, c_gen, c_dl = st.columns([2, 1, 1])
                with c_label:
                    st.markdown(f"<div style='font-size:13px;font-weight:500;color:{GolemanTheme.TEXT}'>{label}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size:11px;color:{GolemanTheme.MUTED}'>{desc}</div>", unsafe_allow_html=True)
                with c_gen:
                    if st.button("Generar", key=f"admin_export_{key}", use_container_width=True):
                        with st.spinner(f"Generando {label}..."):
                            try:
                                file_bytes, filename = export_service.export_module(key, report_start, report_end, selected_users)
                                st.session_state[f"_admin_file_{key}"] = file_bytes
                                st.session_state[f"_admin_filename_{key}"] = filename
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                with c_dl:
                    file_bytes = st.session_state.get(f"_admin_file_{key}")
                    filename = st.session_state.get(f"_admin_filename_{key}")
                    if file_bytes and filename:
                        st.download_button(
                            label="Descargar",
                            data=file_bytes,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"admin_download_{key}",
                            use_container_width=True,
                        )


def _render_process_config():
    st.markdown(GolemanTheme.section_header("Configuracion de Tiempos", "Editar los tiempos por proceso y por modulo"), unsafe_allow_html=True)

    token = st.session_state.get("token")
    service = ProcessConfigFrontendService(token=token)

    if "_proc_config_working" not in st.session_state:
        try:
            config = service.get_config()
            st.session_state["_proc_config_working"] = config.get("processes", [])
            mt = config.get("module_times", {})
            st.session_state["_proc_module_times"] = {
                "legalizations": mt.get("legalizations", 90),
                "billing": mt.get("billing", 45),
                "rips": mt.get("rips", 45),
            }
        except Exception as e:
            st.error(f"Error al cargar configuracion: {e}")
            return

    processes = st.session_state["_proc_config_working"]
    module_times = st.session_state["_proc_module_times"]

    def _collect_from_session():
        procs = []
        for i in range(max(0, len(processes))):
            name = st.session_state.get(f"proc_name_{i}", "").strip()
            secs = st.session_state.get(f"proc_sec_{i}", 60)
            if name:
                procs.append({"name": name, "seconds": secs})
        return procs or [{"name": "AUDITAR CUENTAS", "seconds": 180}]

    def _clear_widget_keys():
        for k in list(st.session_state.keys()):
            if k.startswith("proc_name_") or k.startswith("proc_sec_"):
                del st.session_state[k]

    def _save_all(procs, mt=None):
        if mt is None:
            mt = module_times
        st.session_state["_proc_config_working"] = procs
        st.session_state["_proc_module_times"] = mt
        try:
            service.update_config(procs, mt)
        except Exception as e:
            st.error(f"Error al guardar: {e}")

    # --- Module times ---
    st.markdown(f"<div style='font-size:13px;font-weight:600;color:{GolemanTheme.TEXT};margin-bottom:8px'>Tiempos por Modulo (segundos por registro)</div>", unsafe_allow_html=True)

    col_leg, col_bill, col_rips = st.columns(3)
    with col_leg:
        new_leg = st.number_input("Legalizaciones", value=module_times.get("legalizations", 90), min_value=1, key="mt_leg")
    with col_bill:
        new_bill = st.number_input("Facturacion Electronica", value=module_times.get("billing", 45), min_value=1, key="mt_bill")
    with col_rips:
        new_rips = st.number_input("RIPS", value=module_times.get("rips", 45), min_value=1, key="mt_rips")

    mt_changed = (new_leg != module_times.get("legalizations") or
                  new_bill != module_times.get("billing") or
                  new_rips != module_times.get("rips"))
    if mt_changed:
        module_times["legalizations"] = new_leg
        module_times["billing"] = new_bill
        module_times["rips"] = new_rips

    # --- Processes ---
    st.markdown("---")
    st.markdown(f"<div style='font-size:13px;font-weight:600;color:{GolemanTheme.TEXT};margin-bottom:8px'>Procesos Administrativos (segundos por registro)</div>", unsafe_allow_html=True)

    for i, proc in enumerate(processes):
        col_name, col_seconds, col_del = st.columns([3, 1.5, 0.8])
        with col_name:
            st.text_input("Nombre", value=proc.get("name", ""), key=f"proc_name_{i}", label_visibility="collapsed")
        with col_seconds:
            st.number_input("Segundos", value=proc.get("seconds", 60), min_value=1, key=f"proc_sec_{i}", label_visibility="collapsed")
        with col_del:
            if st.button("✖", key=f"proc_del_{i}", help=f"Eliminar {proc.get('name', '')}", use_container_width=True):
                st.session_state["_proc_del_idx"] = i
                st.rerun()

    del_idx = st.session_state.pop("_proc_del_idx", None)
    if del_idx is not None:
        procs = _collect_from_session()
        if 0 <= del_idx < len(procs):
            del procs[del_idx]
        if not procs:
            procs = [{"name": "AUDITAR CUENTAS", "seconds": 180}]
        _clear_widget_keys()
        _save_all(procs, module_times)
        st.rerun()

    col_save, col_add = st.columns([1, 1])
    with col_save:
        if st.button("Guardar cambios", type="primary", use_container_width=True):
            procs = _collect_from_session()
            _save_all(procs, module_times)
            st.success("Configuracion actualizada correctamente.")
            st.rerun()
    with col_add:
        if st.button("+ Agregar proceso", use_container_width=True):
            processes.append({"name": "", "seconds": 60})
            st.rerun()


def _render_billers_editor():
    st.markdown(GolemanTheme.section_header("Gestión de Facturadores", "Agregar, editar o eliminar facturadores del sistema"), unsafe_allow_html=True)

    api = BillersAdminApi()

    if "_billers_list" not in st.session_state:
        try:
            data = api.list_billers()
            st.session_state["_billers_list"] = data.get("facturadores", [])
        except Exception as e:
            st.error(f"Error al cargar facturadores: {e}")
            return

    billers = st.session_state["_billers_list"]

    has_changes = False

    for i, b in enumerate(billers):
        col_name, col_doc, col_rol, col_del = st.columns([3, 2, 1.5, 0.8])
        with col_name:
            new_name = st.text_input("Nombre", value=b.get("NOMBRE", ""), key=f"b_name_{i}", label_visibility="collapsed")
            if new_name != b.get("NOMBRE", ""):
                billers[i]["NOMBRE"] = new_name
                has_changes = True
        with col_doc:
            new_doc = st.text_input("Documento", value=str(b.get("DOCUMENTO", "")), key=f"b_doc_{i}", label_visibility="collapsed")
            if new_doc != str(b.get("DOCUMENTO", "")):
                billers[i]["DOCUMENTO"] = new_doc
                has_changes = True
        with col_rol:
            roles_opts = ["ANALISTA", "AUXILIAR"]
            idx = roles_opts.index(b.get("ROL", "ANALISTA")) if b.get("ROL", "ANALISTA") in roles_opts else 0
            new_rol = st.selectbox("Rol", roles_opts, index=idx, key=f"b_rol_{i}", label_visibility="collapsed")
            if new_rol != b.get("ROL", ""):
                billers[i]["ROL"] = new_rol
                has_changes = True
        with col_del:
            if st.button("✖", key=f"b_del_{i}", help=f"Eliminar {b.get('NOMBRE', '')}", use_container_width=True):
                st.session_state["_biller_del"] = i
                st.rerun()

    del_idx = st.session_state.pop("_biller_del", None)
    if del_idx is not None:
        del billers[del_idx]
        has_changes = True
        st.session_state["_billers_list"] = billers
        st.rerun()

    col_save, col_add = st.columns([1, 1])
    with col_save:
        if st.button("Guardar cambios", type="primary", use_container_width=True, key="btn_save_billers"):
            try:
                api.update_billers(billers)
                st.session_state.pop("_billers_list", None)
                st.success("Facturadores actualizados correctamente.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {e}")
    with col_add:
        if st.button("+ Agregar facturador", use_container_width=True, key="btn_add_biller"):
            billers.append({"NOMBRE": "", "DOCUMENTO": "", "ROL": "ANALISTA"})
            st.session_state["_billers_list"] = billers
            st.rerun()

    if has_changes:
        st.info("Hay cambios sin guardar. Usa el botón 'Guardar cambios' para persistirlos.")


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

    tab_users, tab_billers, tab_reports, tab_config = st.tabs([
        "👥 Gestión de Usuarios",
        "👤 Facturadores",
        "📥 Descarga de Informes",
        "⚙️ Configuración de Tiempos",
    ])

    with tab_users:
        _render_users_management()

    with tab_billers:
        _render_billers_editor()

    with tab_reports:
        _render_reports_download()

    with tab_config:
        _render_process_config()
