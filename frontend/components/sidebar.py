"""
ui/sidebar.py — Goleman IPS
============================
Sidebar con logo real (base64), usuario del token cacheado,
rol desde session_state y navegación minimalista.
Estilos en GolemanTheme.inject().
"""

import base64
from pathlib import Path

import pandas as pd
import streamlit as st

from frontend.api.data_api import DataApi
from frontend.services.auth_service import AuthFrontendService


# ─────────────────────────────────────────────────────────────────────────────
# Módulos registrados
# ─────────────────────────────────────────────────────────────────────────────

_MODULES = [
    ("📋", "Legalizaciones",     "legalizations_df"),
    ("📄", "RIPS",               "rips_df"),
    ("📋", "Radicación",         "electronic_billing_df"),
    ("💰", "Fact. Electrónica",  "electronic_billing_df"),
    ("⚙️", "Procesos adm.",      "administrative_processes_df")
]

# ─────────────────────────────────────────────────────────────────────────────
# Logo real cacheado en memoria
# ─────────────────────────────────────────────────────────────────────────────

_LOGO_CACHE: str | None = None


def _get_logo_b64() -> str:
    global _LOGO_CACHE
    if _LOGO_CACHE is not None:
        return _LOGO_CACHE
    logo_path = (
            Path(__file__).resolve().parent.parent / "assets" / "LOGO_OSCURO.svg"
    )
    with open(logo_path, "rb") as f:
        _LOGO_CACHE = base64.b64encode(f.read()).decode()
    return _LOGO_CACHE


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_len(key: str) -> int | None:
    df = st.session_state.get(key)
    if df is not None and not df.empty:
        return len(df)
    return None


def _get_current_user() -> dict:
    if "user" in st.session_state and st.session_state["user"]:
        u = st.session_state["user"]
        return {
            "username": u.get("username") or u.get("email") or "Usuario",
            "role": u.get("role") or "Sin rol",
        }
    try:
        service = AuthFrontendService()
        user = service.get_current_user()
        result = {
            "username": user.username or user.email or "Usuario",
            "role":     getattr(user, "role", "Sin rol") or "Sin rol",
        }
    except Exception:
        result = {"username": "Usuario", "role": "Sin rol"}
    return result


def _get_initials(name: str) -> str:
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return name[0].upper() if name else "U"


def _reload_data() -> None:
    try:
        data = DataApi().load()
    except Exception:
        st.error("No se pudieron recargar los datos.")
        return
    for key in ("legalizations_df", "rips_df", "electronic_billing_df",
                "billers_df", "administrative_processes_df"):
        st.session_state[key] = data.get(key)
    st.session_state["ultima_actualizacion"] = pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
    st.rerun()


def _clear_data() -> None:
    for *_, key in _MODULES:
        st.session_state[key] = None
    st.session_state.pop("ultima_actualizacion", None)
    st.session_state.pop("_confirm_clear", None)
    st.rerun()


def _logout() -> None:
    try:
        AuthFrontendService().logout()
    except Exception:
        pass
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Bloques HTML
# ─────────────────────────────────────────────────────────────────────────────

def _html_logo() -> str:
    b64 = _get_logo_b64()
    return (
        f'<div class="g-sidebar-logo">'
        f'<img src="data:image/svg+xml;base64,{b64}" alt="Goleman IPS"/>'
        f'</div>'
    )


def _html_user_pill(user: dict) -> str:
    username = user["username"]
    role     = user["role"]
    initials = _get_initials(username)
    return (
        '<div class="g-user-card">'
        f'<div class="g-user-avatar">{initials}</div>'
        '<div class="g-user-info">'
        f'<div class="g-user-name">{username}</div>'
        f'<span class="g-user-role">{role}</span>'
        '</div>'
        '<div class="g-user-status"></div>'
        '</div>'
    )


_ICON_B64: dict[str, str] | None = None


def _get_icon_data_uri(name: str) -> str:
    global _ICON_B64
    if _ICON_B64 is None:
        _root = Path(__file__).resolve().parent.parent / "assets"
        _ICON_B64 = {}
        for fname in _root.glob("icon_*.svg"):
            key = fname.stem.replace("icon_", "")
            with open(fname, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            _ICON_B64[key] = b64
    b = _ICON_B64.get(name)
    if b:
        return f"data:image/svg+xml;base64,{b}"
    return ""


_ICON_MAP = {
    "Inicio": "home",
    "Legalizaciones": "legalizations",
    "RIPS": "rips",
    "Radicaci\u00f3n": "radicacion",
    "Facturaci\u00f3n": "billing",
    "Procesos Administrativos": "manual_billing",
    "Cargar Archivos": "file_upload",
    "Panel Admin": "file_upload",
}

_nav_items = [
    "Inicio",
    "Legalizaciones",
    "RIPS",
    "Radicaci\u00f3n",
    "Facturaci\u00f3n",
    "Procesos Administrativos",
    "Cargar Archivos",
    "Panel Admin",
]


def _render_nav_items() -> None:
    user = st.session_state.get("user", {})
    role = user.get("role") if user else None
    is_admin = role in ("ADMIN", "SUPERVISOR")
    is_super_admin = role == "ADMIN"

    st.markdown('<div class="g-nav-label">Navegaci\u00f3n</div>', unsafe_allow_html=True)
    for label in _nav_items:
        if label == "Cargar Archivos" and not is_admin:
            continue
        if label == "Panel Admin" and not is_super_admin:
            continue
        if st.button(label, key=f"nav_{label}", use_container_width=True):
            st.session_state["_nav_tab"] = label
            st.rerun()


def _html_footer() -> str:
    ultima = st.session_state.get("ultima_actualizacion")
    ts = f"\u23f1 {ultima}" if ultima else "\u23f1 Sin datos"
    return (
        '<div class="g-sidebar-footer">'
        f'<div class="g-footer-row">v2.0.0</div>'
        f'<div class="g-footer-row">{ts}</div>'
        f'<div class="g-footer-row">Ambiente: Producci\u00f3n</div>'
        '</div>'
    )


# ─────────────────────────────────────────────────────────────────────────────
# Punto de entrada público
# ─────────────────────────────────────────────────────────────────────────────

def render_state_data() -> None:
    user = _get_current_user()

    with st.sidebar:

        st.markdown(_html_logo(), unsafe_allow_html=True)

        st.markdown(_html_user_pill(user), unsafe_allow_html=True)

        _render_nav_items()

        st.markdown('<div id="sb-logout-marker"></div>', unsafe_allow_html=True)
        st.button(
            "Cerrar sesi\u00f3n",
            use_container_width=True,
            key="sb_logout",
            help="Cierra la sesi\u00f3n y vuelve al login",
            on_click=_logout,
        )

        st.markdown(_html_footer(), unsafe_allow_html=True)
