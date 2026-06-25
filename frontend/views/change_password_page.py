"""
Change Password Page — Goleman IPS
First-login forced password change.
"""

import streamlit as st

from frontend.exceptions import ApiException
from frontend.services.auth_service import AuthFrontendService
from ui.goleman_theme import GolemanTheme


def render_change_password_page() -> None:
    GolemanTheme.inject(sidebar=False)

    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background: linear-gradient(135deg, {GolemanTheme.NAVY} 0%, {GolemanTheme.NAVY2} 55%, #0a1a3a 100%) !important;
        min-height: 100vh;
    }}
    [data-testid="stMain"] {{ background: transparent !important; }}
    [data-testid="stMainBlockContainer"] {{
        max-width: 440px !important;
        margin: 0 auto !important;
        padding-top: 10vh !important;
        padding-bottom: 40px !important;
    }}
    [data-testid="stAppViewContainer"]::before {{ display: none !important; }}
    .cp-card {{
        background: {GolemanTheme.WHITE};
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(0,0,0,.35), 0 4px 16px rgba(0,0,0,.2);
    }}
    .cp-header {{
        background: {GolemanTheme.NAVY};
        padding: 28px 28px 24px;
        text-align: center;
    }}
    .cp-header-title {{
        font-size: 18px;
        font-weight: 600;
        color: {GolemanTheme.WHITE};
        margin-bottom: 6px;
    }}
    .cp-header-sub {{
        font-size: 12px;
        color: rgba(255,255,255,.5);
    }}
    .cp-strip {{
        height: 3px;
        background: linear-gradient(90deg, {GolemanTheme.NAVY}, {GolemanTheme.BLUE} 40%, {GolemanTheme.ORANGE});
    }}
    .cp-body {{
        padding: 28px 28px 24px;
        background: {GolemanTheme.WHITE};
    }}
    .cp-title {{
        font-size: 16px;
        font-weight: 600;
        color: {GolemanTheme.NAVY};
        margin-bottom: 4px;
    }}
    .cp-sub {{
        font-size: 12px;
        color: {GolemanTheme.MUTED};
        margin-bottom: 20px;
        line-height: 1.5;
    }}
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
    [data-testid="stMainBlockContainer"] button[kind="primary"] {{
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
    [data-testid="stMainBlockContainer"] button[kind="primary"]:hover {{
        background: #e86a2b !important;
        box-shadow: 0 6px 20px rgba(249,120,56,.45) !important;
    }}
    [data-testid="stMainBlockContainer"] [data-testid="stAlert"] {{
        border-radius: 9px !important;
        font-size: 12px !important;
        margin-top: 8px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="cp-card">
      <div class="cp-header">
        <div class="cp-header-title">Cambiar contraseña</div>
        <div class="cp-header-sub">Goleman IPS</div>
      </div>
      <div class="cp-strip"></div>
      <div class="cp-body">
        <div class="cp-title">Nueva contraseña</div>
        <div class="cp-sub">Por seguridad, debes cambiar tu contraseña antes de continuar. La contraseña debe tener al menos 8 caracteres.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("change_password_form", clear_on_submit=False):
        new_password = st.text_input(
            "NUEVA CONTRASEÑA",
            type="password",
            placeholder="••••••••",
            label_visibility="visible",
        )
        confirm_password = st.text_input(
            "CONFIRMAR CONTRASEÑA",
            type="password",
            placeholder="••••••••",
            label_visibility="visible",
        )

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        submitted = st.form_submit_button(
            "Cambiar contraseña",
            use_container_width=True,
        )

    if submitted:
        if not new_password or not confirm_password:
            st.warning("Todos los campos son obligatorios.")
        elif new_password != confirm_password:
            st.error("Las contraseñas no coinciden.")
        elif len(new_password) < 8:
            st.error("La contraseña debe tener al menos 8 caracteres.")
        else:
            with st.spinner("Cambiando contraseña…"):
                try:
                    service = AuthFrontendService()
                    service.change_password(new_password)
                    st.success("Contraseña cambiada correctamente.")
                    st.rerun()
                except ApiException as e:
                    st.error(e.message)
                except Exception as e:
                    st.error(f"Error inesperado: {e}")
