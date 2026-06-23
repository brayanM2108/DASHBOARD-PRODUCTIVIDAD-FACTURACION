"""
Productivity Dashboard - Main Application
==================================================
Author: Brayan Melo
Version: 2.0
=================================================
Streamlit Application Entry Point
"""

import streamlit as st
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[1]
if str(_root) not in sys.path:
    sys.path.append(str(_root))

_backend_pkg = _root / "backend"
if str(_backend_pkg) not in sys.path:
    sys.path.append(str(_backend_pkg))

from backend.app.utils.config.settings import PAGE_CONFIG
from backend.app.etl.loaders import load_all_persisted_frames_cached, load_billers_master_cached
from frontend.components.file_upload import render_file_upload_section
from frontend.components.global_filters_bar import render_global_filters_bar
from frontend.components.sidebar import render_state_data
from frontend.views.tab_legalizations import render_tab_legalizations
from frontend.views.tab_manual_billing import render_tab_manual_billing
from frontend.views.tab_rips import render_tab_rips
from frontend.views.tab_radicacion import render_tab_radicacion
from frontend.views.billing_electronic_page import render_tab_billing_electronic
from frontend.views.home_page import HomePage

from frontend.views.login_page import render_login_page
from frontend.views.register_page import render_register_page
from frontend.views.admin_panel import render_admin_panel
from frontend.auth.auth_guard import is_authenticated
from ui.goleman_theme import GolemanTheme


def init_session_state():

    if 'initialized' not in st.session_state:
        data = load_all_persisted_frames_cached()

        st.session_state["legalizations_df"] = data.get("legalizations_df")
        st.session_state["rips_df"] = data.get("rips_df")
        st.session_state["billers_df"] = data.get("billers_df")
        st.session_state["electronic_billing_df"] = data.get("electronic_billing_df")
        st.session_state["administrative_processes_df"] = data.get("administrative_processes_df")

        if st.session_state["billers_df"] is None:
            st.session_state["billers_df"] = load_billers_master_cached()

        st.session_state["initialized"] = True


def main():

    st.set_page_config(**PAGE_CONFIG)

    GolemanTheme.inject()

    if not is_authenticated():
        auth_view = st.session_state.get("auth_view", "login")
        if auth_view == "register":
            render_register_page()
        else:
            render_login_page()
        st.stop()

    # Eliminar flag de login después de autenticarse
    st.session_state.pop("_just_logged_in", None)

    init_session_state()

    nav_tab = st.session_state.get("_nav_tab", "Inicio")

    render_state_data()

    if nav_tab != "Cargar Archivos":
        render_global_filters_bar()

    _tab_titles = {
        "Inicio": "Dashboard de Productividad",
        "Legalizaciones": "Legalizaciones",
        "RIPS": "RIPS",
        "Radicación": "Radicación",
        "Facturación": "Facturación Electrónica",
        "Procesos Administrativos": "Procesos Administrativos",
        "Cargar Archivos": "Cargar Archivos",
        "Panel Admin": "Panel de Administración",
    }

    st.markdown(
        f'<div class="g-tab-title">{_tab_titles.get(nav_tab, "Dashboard")}</div>',
        unsafe_allow_html=True,
    )

    if nav_tab == "Inicio":
        HomePage.render()

    elif nav_tab == "Legalizaciones":
        render_tab_legalizations()

    elif nav_tab == "RIPS":
        render_tab_rips()

    elif nav_tab == "Radicación":
        render_tab_radicacion()

    elif nav_tab == "Facturación":
        render_tab_billing_electronic()

    elif nav_tab == "Procesos Administrativos":
        render_tab_manual_billing()

    elif nav_tab == "Cargar Archivos":
        user = st.session_state.get("user", {})
        role = user.get("role") if user else None
        if role in ("ADMIN", "SUPERVISOR"):
            render_file_upload_section()
        else:
            st.warning("No tienes permisos para cargar archivos. Solo el administrador puede hacerlo.")

    elif nav_tab == "Panel Admin":
        render_admin_panel()

if __name__ == "__main__":
    main()
