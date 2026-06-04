"""
Sidebar panel
===========================
Side panel with data status and useful functions.
"""

import streamlit as st
import pandas as pd
from backend.app.etl.loaders import load_all_persisted_frames
from frontend.components.filters import render_user_filter


_MODULES = [
    ("ti-clipboard-list", "PPL",               "ppl_legalizations_df"),
    ("ti-handshake",      "Convenios",          "agreement_legalizations_df"),
    ("ti-receipt",        "Fact. electrónica",  "electronic_billing_df"),
    ("ti-settings",       "Procesos adm.",      "administrative_processes_df"),
    ("ti-users",          "Facturadores",       "billers_df"),
]

_LEG_KEYS = {"ppl_legalizations_df", "agreement_legalizations_df"}


_SIDEBAR_CSS = """
<style>
[data-testid="stSidebar"] { padding-top: 0.5rem; }

.sb-section-label {
    font-size: 10px;
    font-weight: 500;
    color: var(--text-color);
    opacity: 0.45;
    letter-spacing: .07em;
    text-transform: uppercase;
    margin: 0 0 8px;
}

.sb-mod-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 6px;
    border-radius: 6px;
    margin-bottom: 2px;
}

.sb-mod-name { font-size: 12px; flex: 1; }

.sb-pill {
    font-size: 10px;
    font-weight: 500;
    padding: 1px 7px;
    border-radius: 10px;
    white-space: nowrap;
}

.sb-pill-ok  { background: #EAF3DE; color: #3B6D11; }
	sb-pill-nil { background: rgba(128,128,128,.12); color: rgba(128,128,128,.7); }

	sb-timestamp {
		font-size: 11px;
		opacity: 0.45;
		margin-top: 4px;
	}
</style>
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_len(key: str) -> int | None:
    df = st.session_state.get(key)
    if df is not None and not df.empty:
        return len(df)
    return None


def _reload_data() -> None:
    data = load_all_persisted_frames()
    st.session_state.update({
        "ppl_legalizations_df":        data.get("ppl_legalizations"),
        "agreement_legalizations_df":  data.get("agreement_legalizations"),
        "electronic_billing_df":       data.get("electronic_billing"),
        "billers_df":                  data.get("billers"),
        "administrative_processes_df": data.get("administrative_processes"),
        "ultima_actualizacion":        pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
    })
    st.cache_data.clear()
    st.rerun()


def _clear_data() -> None:
    for *_, key in _MODULES:
        st.session_state[key] = None
    st.session_state.pop("ultima_actualizacion", None)
    st.session_state.pop("_confirm_clear", None)
    st.rerun()


def _render_modules() -> None:
    st.markdown('<p class="sb-section-label">Módulos</p>', unsafe_allow_html=True)

    for _icon, nombre, key in _MODULES:
        n = _get_len(key)
        if n is not None:
            pill = f'<span class="sb-pill sb-pill-ok">{n:,}</span>'
        else:
            pill = '<span class="sb-pill sb-pill-nil">Sin datos</span>'

        st.markdown(
            f'<div class="sb-mod-row">'
            f'<span class="sb-mod-name">{nombre}</span>'
            f'{pill}'
            f'</div>',
            unsafe_allow_html=True,
        )


def _render_summary() -> None:
    st.markdown('<p class="sb-section-label">Resumen</p>', unsafe_allow_html=True)

    total_leg = sum(
        _get_len(k) or 0 for k in ("ppl_legalizations_df", "agreement_legalizations_df")
    )

    total_bill_value = 0.0
    billing_df = st.session_state.get("electronic_billing_df")
    if billing_df is not None and not billing_df.empty and "VALOR TERCERO" in billing_df.columns:
        total_bill_value = pd.to_numeric(
            billing_df["VALOR TERCERO"], errors="coerce"
        ).fillna(0).sum()

    st.metric("Legalizaciones", f"{total_leg:,}")
    st.metric("Facturación", f"${total_bill_value:,.0f}")


def _render_global_filters() -> None:
    """
    Filtros globales de fecha y usuario.
    Los valores se guardan en session_state con prefijo 'global_'
    para que cada tab los lea sin duplicar widgets.
    """
    st.markdown('<p class="sb-section-label">Filtros globales</p>', unsafe_allow_html=True)

    # Derivar min/max de fechas desde los datos disponibles
    min_date = pd.Timestamp("2026-01-01").date()
    max_date = pd.Timestamp.now().date()

    for *_, key in _MODULES:
        df = st.session_state.get(key)
        if df is None or df.empty:
            continue
        for col in ("FECHA", "fecha", "FECHA_SERVICIO"):
            if col in df.columns:
                parsed = pd.to_datetime(df[col], errors="coerce").dropna()
                if not parsed.empty:
                    min_date = min(min_date, parsed.min().date())
                    max_date = max(max_date, parsed.max().date())
                break

    st.session_state["global_start_date"] = st.date_input(
        "Fecha inicio",
        value=st.session_state.get("global_start_date", min_date),
        min_value=min_date,
        max_value=max_date,
        key="sb_start_date",
    )

    st.session_state["global_end_date"] = st.date_input(
        "Fecha fin",
        value=st.session_state.get("global_end_date", max_date),
        min_value=min_date,
        max_value=max_date,
        key="sb_end_date",
    )

    selected_user = render_user_filter(
        st.session_state.get("billers_df"),
        key_prefix="sb",
    )
    st.session_state["global_user"] = selected_user

    if st.button("Aplicar filtros", use_container_width=True):
        st.rerun()


def _render_actions() -> None:
    st.markdown('<p class="sb-section-label">Acciones</p>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        if st.button("🔄 Recargar", use_container_width=True, help="Recarga datos persistidos"):
            _reload_data()

    with c2:
        if not st.session_state.get("_confirm_clear", False):
            if st.button("🗑️ Limpiar", use_container_width=True, help="Borra todos los datos"):
                st.session_state["_confirm_clear"] = True
                st.rerun()
        else:
            st.warning("¿Confirmar borrado?")
            cy, cn = st.columns(2)
            with cy:
                if st.button("Sí", use_container_width=True, type="primary"):
                    _clear_data()
            with cn:
                if st.button("No", use_container_width=True):
                    st.session_state["_confirm_clear"] = False
                    st.rerun()


def _render_timestamp() -> None:
    ultima = st.session_state.get("ultima_actualizacion")
    texto = f"🕐 Actualizado: {ultima}" if ultima else "🕐 Sin actualizaciones"
    st.markdown(f'<p class="sb-timestamp">{texto}</p>', unsafe_allow_html=True)


def render_state_data() -> None:
    """Renderiza el sidebar completo."""
    st.markdown(_SIDEBAR_CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.title("Panel de control")
        st.divider()

        _render_modules()
        st.divider()

        _render_summary()
        st.divider()

        _render_global_filters()
        st.divider()

        _render_actions()
        st.divider()

        _render_timestamp()
