"""
ui/auth/login.py
================
Login rediseñado con paleta Goleman IPS y GolemanTheme centralizado.
"""

import base64
from pathlib import Path

import streamlit as st

from frontend.exceptions import ApiException, UnauthorizedException, UserNotActiveException
from frontend.services.auth_service import AuthFrontendService
from ui.goleman_theme import GolemanTheme

_LOGO_CACHE: str | None = None


def _get_logo_b64() -> str:
    global _LOGO_CACHE
    if _LOGO_CACHE is not None:
        return _LOGO_CACHE
    logo_path = (
        Path(__file__).resolve().parent.parent / "assets" / "LOGO_OSCURO.svg"
    )
    svg = logo_path.read_text(encoding="utf-8")
    if svg.startswith("<?xml"):
        svg = svg.split("?>", 1)[-1].strip()
    _LOGO_CACHE = base64.b64encode(svg.encode("utf-8")).decode()
    return _LOGO_CACHE


def render_login_page() -> None:
    GolemanTheme.inject(sidebar=False)
    _inject_login_css()
    _render_layout()


# ─────────────────────────────────────────────────────────────────────────────
# CSS específico del login
# ─────────────────────────────────────────────────────────────────────────────

def _inject_login_css() -> None:
    st.markdown(f"""
    <style>
    /* ── Fondo de la página centrado ── */
    [data-testid="stAppViewContainer"] {{
        background: linear-gradient(
            135deg,
            {GolemanTheme.NAVY} 0%,
            {GolemanTheme.NAVY2} 55%,
            #0a1a3a 100%
        ) !important;
        min-height: 100vh;
    }}
    [data-testid="stMain"] {{
        background: transparent !important;
    }}
    [data-testid="stMainBlockContainer"] {{
        max-width: 440px !important;
        margin: 0 auto !important;
        padding-top: 6vh !important;
        padding-bottom: 40px !important;
    }}

    /* ── Quitar franja del tema general en esta página ── */
    [data-testid="stAppViewContainer"]::before {{
        display: none !important;
    }}

    /* ── Card principal ── */
    .login-card {{
        background: {GolemanTheme.WHITE};
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(0,0,0,.35), 0 4px 16px rgba(0,0,0,.2);
    }}

    /* ── Header de la card (navy) ── */
    .login-header {{
        background: {GolemanTheme.NAVY};
        padding: 28px 28px 24px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
        position: relative;
        overflow: hidden;
    }}
    .login-header::before {{
        content: '';
        position: absolute;
        top: -60px; right: -60px;
        width: 200px; height: 200px;
        border-radius: 50%;
        background: rgba(167,226,255,.05);
    }}
    .login-header::after {{
        content: '';
        position: absolute;
        bottom: -40px; left: -40px;
        width: 150px; height: 150px;
        border-radius: 50%;
        background: rgba(249,120,56,.06);
    }}
    .login-logo {{
        width: 180px;
        height: auto;
        position: relative;
        z-index: 1;
    }}
    .login-tagline {{
        font-size: 12px;
        color: rgba(255,255,255,.4);
        letter-spacing: .06em;
        text-transform: uppercase;
        position: relative;
        z-index: 1;
    }}

    /* ── Franja de color ── */
    .login-strip {{
        height: 3px;
        background: linear-gradient(90deg, {GolemanTheme.NAVY}, {GolemanTheme.BLUE} 40%, {GolemanTheme.ORANGE});
    }}

    /* ── Cuerpo del formulario ── */
    .login-body {{
        padding: 28px 28px 24px;
        background: {GolemanTheme.WHITE};
    }}
    .login-title {{
        font-size: 18px;
        font-weight: 600;
        color: {GolemanTheme.NAVY};
        margin-bottom: 4px;
    }}
    .login-sub {{
        font-size: 12px;
        color: {GolemanTheme.MUTED};
        margin-bottom: 20px;
    }}

    /* ── Footer de la card ── */
    .login-footer {{
        padding: 14px 28px 20px;
        border-top: 0.5px solid {GolemanTheme.BORDER};
        background: {GolemanTheme.BG};
        text-align: center;
    }}
    .login-footer-text {{
        font-size: 11px;
        color: {GolemanTheme.MUTED};
    }}

    /* ── Inputs dentro del login ── */
    [data-testid="stMainBlockContainer"] [data-testid="stTextInput"] input {{
        border: 1px solid {GolemanTheme.BORDER} !important;
        border-radius: 9px !important;
        background: {GolemanTheme.BG} !important;
        padding: 10px 12px !important;
        font-size: 13px !important;
        color: {GolemanTheme.TEXT} !important;
        height: 44px !important;
        transition: border-color .15s, box-shadow .15s !important;
    }}
    [data-testid="stMainBlockContainer"] [data-testid="stTextInput"] input:focus {{
        border-color: {GolemanTheme.BLUE} !important;
        box-shadow: 0 0 0 3px rgba(21,101,192,.12) !important;
        background: {GolemanTheme.WHITE} !important;
    }}
    [data-testid="stMainBlockContainer"] [data-testid="stTextInput"] label {{
        font-size: 12px !important;
        font-weight: 500 !important;
        color: {GolemanTheme.MUTED} !important;
        letter-spacing: .03em !important;
        margin-bottom: 4px !important;
    }}

    /* ── Botón submit (Iniciar sesión) — naranja ── */
    [data-testid="stFormSubmitButton"] > button {{
        background: {GolemanTheme.ORANGE} !important;
        color: {GolemanTheme.WHITE} !important;
        border: none !important;
        border-radius: 10px !important;
        height: 48px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        width: 100% !important;
        letter-spacing: .02em !important;
        box-shadow: 0 4px 14px rgba(249,120,56,.35) !important;
        transition: background .15s, box-shadow .15s !important;
    }}
    [data-testid="stFormSubmitButton"] > button:hover {{
        background: #e86a2b !important;
        box-shadow: 0 6px 20px rgba(249,120,56,.45) !important;
    }}
    [data-testid="stFormSubmitButton"] > button:active {{
        background: #d05a20 !important;
        box-shadow: none !important;
    }}

    /* ── Botón secundario (Registrarse) — navy ghost ── */
    [data-testid="stMainBlockContainer"] [data-testid="stButton"] > button {{
        background: transparent !important;
        color: {GolemanTheme.MUTED} !important;
        border: none !important;
        font-size: 12px !important;
        font-weight: 400 !important;
        height: auto !important;
        padding: 6px 0 !important;
        text-decoration: underline !important;
        text-underline-offset: 3px !important;
        box-shadow: none !important;
    }}
    [data-testid="stMainBlockContainer"] [data-testid="stButton"] > button:hover {{
        color: {GolemanTheme.BLUE} !important;
        background: transparent !important;
    }}

    /* ── Form: sin bordes ni fondos extras ── */
    [data-testid="stForm"] {{
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        box-shadow: none !important;
    }}

    /* ── Alertas dentro del login ── */
    [data-testid="stMainBlockContainer"] [data-testid="stAlert"] {{
        border-radius: 9px !important;
        font-size: 12px !important;
        margin-top: 8px !important;
    }}
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Layout del formulario
# ─────────────────────────────────────────────────────────────────────────────

def _render_layout() -> None:
    logo_b64 = _get_logo_b64()

    # ── Header de la card ──
    st.markdown(f"""
    <div class="login-card">
      <div class="login-header">
        <img
          src="data:image/svg+xml;base64,{logo_b64}"
          class="login-logo"
          alt="Goleman IPS"
        />
        <div class="login-tagline">Dashboard de productividad</div>
      </div>
      <div class="login-strip"></div>
      <div class="login-body">
        <div class="login-title">Iniciar sesión</div>
        <div class="login-sub">Ingresa con tu cuenta institucional</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Formulario (widgets Streamlit nativos) ──
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input(
            "CORREO INSTITUCIONAL",
            placeholder="usuario@ipsgoleman.com.co",
            label_visibility="visible",
        )
        password = st.text_input(
            "CONTRASEÑA",
            type="password",
            placeholder="••••••••",
            label_visibility="visible",
        )

        # Espacio antes del botón
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        submitted = st.form_submit_button(
            "Iniciar sesión",
            use_container_width=True,
        )

    # ── Lógica de autenticación ──
    if submitted:
        if not email or not password:
            st.warning("El correo y la contraseña son obligatorios.")
        else:
            with st.spinner("Verificando credenciales…"):
                try:
                    service = AuthFrontendService()
                    service.login(email, password)
                    st.rerun()

                except UserNotActiveException:
                    st.error("Tu cuenta no está activa. Contacta al administrador.")
                except UnauthorizedException:
                    st.error("Credenciales inválidas. Verifica tu correo y contraseña.")
                except ApiException as e:
                    st.error(e.message)
                except Exception as e:
                    st.error(f"Error inesperado: {e}")

    # ── Footer: ir a registro ──
    st.markdown(f"""
    <div style="text-align:center;padding:4px 0 2px">
      <span style="font-size:12px;color:{GolemanTheme.MUTED}">
        ¿No tienes cuenta?
      </span>
    </div>
    """, unsafe_allow_html=True)

    if st.button(
            "Registrate",
            use_container_width=True,
            key="go_to_register",
    ):
        st.session_state["auth_view"] = "register"
        st.rerun()

    # ── Nota de pie ──
    st.markdown(f"""
    <div style="text-align:center;margin-top:16px">
      <span style="font-size:10px;color:rgba(255,255,255,.2)">
        Goleman IPS · Acceso restringido al personal autorizado
      </span>
    </div>
    """, unsafe_allow_html=True)