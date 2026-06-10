"""
ui/auth/register.py
===================
Registro rediseñado — mismo estilo que login, paleta Goleman IPS.
"""

import base64
from pathlib import Path

import streamlit as st

from frontend.exceptions import ApiException
from frontend.services.auth_service import AuthFrontendService
from ui.goleman_theme import GolemanTheme

_ROLES = ["Facturador", "Auditor", "Administrativo", "Coordinador"]
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


def _validate(
        nombre: str,
        apellido: str,
        documento: str,
        email: str,
        password: str,
        password2: str,
        terminos: bool,
) -> list[str]:
    errors = []
    if not nombre.strip():
        errors.append("El nombre es obligatorio.")
    if not apellido.strip():
        errors.append("El apellido es obligatorio.")
    if not documento.strip():
        errors.append("El número de documento es obligatorio.")
    elif not documento.strip().isdigit():
        errors.append("El documento debe contener solo números.")
    elif len(documento.strip()) < 5:
        errors.append("El documento debe tener al menos 5 dígitos.")
    if not email.strip() or "@" not in email:
        errors.append("Ingresa un correo institucional válido.")
    if len(password) < 8:
        errors.append("La contraseña debe tener al menos 8 caracteres.")
    if password != password2:
        errors.append("Las contraseñas no coinciden.")
    if not terminos:
        errors.append("Debes aceptar los términos de uso.")
    return errors


# ─────────────────────────────────────────────────────────────────────────────
# Punto de entrada
# ─────────────────────────────────────────────────────────────────────────────

def render_register_page() -> None:
    GolemanTheme.inject(sidebar=False)
    _inject_register_css()
    _render_layout()


# ─────────────────────────────────────────────────────────────────────────────
# CSS — idéntico al login más ajustes propios del registro
# ─────────────────────────────────────────────────────────────────────────────

def _inject_register_css() -> None:
    st.markdown(f"""
    <style>
    /* ── Fondo degradado (igual que login) ── */
    [data-testid="stAppViewContainer"] {{
        background: linear-gradient(
            135deg,
            {GolemanTheme.NAVY}  0%,
            {GolemanTheme.NAVY2} 55%,
            #0a1a3a              100%
        ) !important;
        min-height: 100vh;
    }}
    [data-testid="stMain"] {{
        background: transparent !important;
    }}

    /* ── Card más ancha por los campos extra ── */
    [data-testid="stMainBlockContainer"] {{
        max-width: 520px !important;
        margin: 0 auto !important;
        padding-top: 4vh !important;
        padding-bottom: 40px !important;
    }}

    /* ── Sin franja superior del tema general ── */
    [data-testid="stAppViewContainer"]::before {{
        display: none !important;
    }}

    /* ── Inputs ── */
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
    }}

    /* ── Selectbox de rol ── */
    [data-testid="stMainBlockContainer"] [data-testid="stSelectbox"] > div > div {{
        border: 1px solid {GolemanTheme.BORDER} !important;
        border-radius: 9px !important;
        background: {GolemanTheme.BG} !important;
        font-size: 13px !important;
        min-height: 44px !important;
    }}
    [data-testid="stMainBlockContainer"] [data-testid="stSelectbox"] label {{
        font-size: 12px !important;
        font-weight: 500 !important;
        color: {GolemanTheme.MUTED} !important;
        letter-spacing: .03em !important;
    }}

    /* ── Checkbox de términos ── */
    [data-testid="stMainBlockContainer"] [data-testid="stCheckbox"] label {{
        font-size: 12px !important;
        color: {GolemanTheme.MUTED} !important;
        line-height: 1.5 !important;
    }}
    [data-testid="stMainBlockContainer"] [data-testid="stCheckbox"] {{
        accent-color: {GolemanTheme.BLUE} !important;
    }}

    /* ── Botón submit (naranja, igual que login) ── */
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

    /* ── Botón "Ya tienes cuenta" — ghost ── */
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

    /* ── Form sin bordes extra ── */
    [data-testid="stForm"] {{
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        box-shadow: none !important;
    }}

    /* ── Alertas ── */
    [data-testid="stMainBlockContainer"] [data-testid="stAlert"] {{
        border-radius: 9px !important;
        font-size: 12px !important;
        margin-top: 6px !important;
    }}
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Layout
# ─────────────────────────────────────────────────────────────────────────────

def _render_layout() -> None:
    logo_b64 = _get_logo_b64()

    # ── Header de la card (idéntico al login, título distinto) ──
    st.markdown(f"""
    <div style="
        background:{GolemanTheme.NAVY};
        border-radius:16px 16px 0 0;
        padding:24px 28px 20px;
        display:flex;
        flex-direction:column;
        align-items:center;
        gap:8px;
        position:relative;
        overflow:hidden;
        box-shadow:0 20px 60px rgba(0,0,0,.35),0 4px 16px rgba(0,0,0,.2);
    ">
      <div style="
          position:absolute;top:-60px;right:-60px;
          width:200px;height:200px;border-radius:50%;
          background:rgba(167,226,255,.05)">
      </div>
      <div style="
          position:absolute;bottom:-40px;left:-40px;
          width:150px;height:150px;border-radius:50%;
          background:rgba(249,120,56,.06)">
      </div>
      <img
        src="data:image/svg+xml;base64,{logo_b64}"
        style="width:160px;height:auto;position:relative;z-index:1"
        alt="Goleman IPS"
      />
      <div style="
          font-size:12px;
          color:rgba(255,255,255,.4);
          letter-spacing:.06em;
          text-transform:uppercase;
          position:relative;z-index:1;
      ">Crear cuenta</div>
    </div>

    <!-- Franja de color -->
    <div style="
        height:3px;
        background:linear-gradient(90deg,{GolemanTheme.NAVY},{GolemanTheme.BLUE} 40%,{GolemanTheme.ORANGE});
    "></div>

    <!-- Cuerpo blanco -->
    <div style="
        background:{GolemanTheme.WHITE};
        border-radius:0 0 16px 16px;
        padding:24px 28px 20px;
        box-shadow:0 20px 60px rgba(0,0,0,.35),0 4px 16px rgba(0,0,0,.2);
        margin-bottom:0;
    ">
      <div style="font-size:16px;font-weight:600;color:{GolemanTheme.NAVY};margin-bottom:2px">
        Registro de usuario
      </div>
      <div style="font-size:12px;color:{GolemanTheme.MUTED};margin-bottom:18px">
        Completa los datos para solicitar acceso
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Formulario (widgets nativos Streamlit) ──
    with st.form("register_form", clear_on_submit=False):

        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("NOMBRE", placeholder="Maria")
        with c2:
            apellido = st.text_input("APELLIDO", placeholder="López")

        documento = st.text_input(
            "NÚMERO DE DOCUMENTO",
            placeholder="1234567890",
        )

        email = st.text_input(
            "CORREO INSTITUCIONAL",
            placeholder="usuario@ipsgoleman.com.co",
        )

        rol = st.selectbox("ROL", _ROLES)

        c1, c2 = st.columns(2)
        with c1:
            password = st.text_input(
                "CONTRASEÑA",
                type="password",
                placeholder="Mínimo 8 caracteres",
            )
        with c2:
            password2 = st.text_input(
                "CONFIRMAR CONTRASEÑA",
                type="password",
                placeholder="Repite la contraseña",
            )

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        terminos = st.checkbox(
            "Acepto los términos de uso y la política de privacidad de Goleman IPS"
        )

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        submitted = st.form_submit_button(
            "Crear cuenta",
            use_container_width=True,
        )

    # ── Lógica de registro ──
    if submitted:
        errors = _validate(nombre, apellido, documento, email, password, password2, terminos)
        if errors:
            for err in errors:
                st.error(err)
        else:
            with st.spinner("Creando cuenta…"):
                try:
                    service = AuthFrontendService()
                    service.register(
                        email=email.strip(),
                        document=documento.strip(),
                        username=f"{nombre.strip()} {apellido.strip()}",
                        password=password,
                        role=rol,
                    )
                    st.success("Cuenta creada. Ya puedes iniciar sesión.")
                    st.session_state["auth_view"] = "login"
                    st.rerun()

                except ApiException as e:
                    st.error(e.message)
                except Exception as e:
                    st.error(f"Error inesperado: {e}")

    # ── Footer: ir a login ──
    st.markdown(f"""
    <div style="text-align:center;padding:4px 0 2px">
      <span style="font-size:12px;color:rgba(255,255,255,.35)">
        ¿Ya tienes cuenta?
      </span>
    </div>
    """, unsafe_allow_html=True)

    if st.button(
            "Inicia sesión",
            use_container_width=True,
            key="go_to_login",
    ):
        st.session_state["auth_view"] = "login"
        st.rerun()

    st.markdown(f"""
    <div style="text-align:center;margin-top:16px">
      <span style="font-size:10px;color:rgba(255,255,255,.2)">
        Goleman IPS · Acceso restringido al personal autorizado
      </span>
    </div>
    """, unsafe_allow_html=True)