"""
File Upload Section — Goleman IPS.
Paleta y estilos desde GolemanTheme.
"""

import pandas as pd
import streamlit as st

from frontend.api.data_api import DataApi
from frontend.components.components import show_error_message, show_success_message, show_warning_message
from ui.goleman_theme import GolemanTheme

_FILE_KEY_MAP = {
    "legalizations_df": "Legalizaciones",
    "electronic_billing_df": "FacturacionElectronica",
    "rips_df": "Rips",
    "billers_df": "Facturadores",
}

# ─────────────────────────────────────────────────────────────────────────────
# Configuración de módulos de carga
# ─────────────────────────────────────────────────────────────────────────────

_UPLOAD_MODULES = [
    {
        "section":    "Legalizaciones",
        "icon":       "ti-clipboard-list",
        "hint":       "",
        "files": [
            {
                "key":      "legalizations_df",
                "label":    "Legalizaciones (PPL + Convenios)",
                "hint":     "",
            },
        ],
    },
    {
        "section":    "Facturación Electrónica",
        "icon":       "ti-receipt",
        "hint":       "",
        "files": [
            {
                "key":      "electronic_billing_df",
                "label":    "Facturación Electrónica",
                "hint":     "",
            },
        ],
    },
    {
        "section":    "RIPS",
        "icon":       "ti-file-text",
        "hint":       "Registros individuales de prestación de servicios",
        "files": [
            {
                "key":      "rips_df",
                "label":    "RIPS",
                "hint":     "Registros individuales de prestación de servicios",
            },
        ],
    },
    {
        "section":    "Facturadores",
        "icon":       "ti-users",
        "hint":       "",
        "files": [
            {
                "key":      "billers_df",
                "label":    "Archivo de facturadores",
                "hint":     "Se gestiona desde el Panel Admin",
                "optional": True,
            },
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers HTML
# ─────────────────────────────────────────────────────────────────────────────

def _status_chip(loaded: bool, optional: bool = False) -> str:
    if loaded:
        return (
            f"<span style='font-size:10px;padding:2px 8px;border-radius:20px;"
            f"background:{GolemanTheme.SUCCESS_LIGHT};color:{GolemanTheme.SUCCESS};"
            f"border:0.5px solid #C6F6D5;font-weight:500'>\u2713 Cargado</span>"
        )
    if optional:
        return (
            f"<span style='font-size:10px;padding:2px 8px;border-radius:20px;"
            f"background:{GolemanTheme.WARNING_LIGHT};color:{GolemanTheme.WARNING};"
            f"border:0.5px solid #FAF089;font-weight:500'>\u26a0 Recomendado</span>"
        )
    return (
        f"<span style='font-size:10px;padding:2px 8px;border-radius:20px;"
        f"background:{GolemanTheme.BG};color:{GolemanTheme.MUTED};"
        f"border:0.5px solid {GolemanTheme.BORDER}'>Sin datos</span>"
    )


def _progress_item(filename: str, subtitle: str, kind: str) -> str:
    if kind == "ok":
        icon_bg  = GolemanTheme.SUCCESS_LIGHT
        icon     = "ti-check"
        icon_col = GolemanTheme.SUCCESS
        bar_col  = GolemanTheme.SUCCESS
        label    = "Completo"
        lbl_col  = GolemanTheme.SUCCESS
    else:
        icon_bg  = GolemanTheme.DANGER_LIGHT
        icon     = "ti-alert-circle"
        icon_col = GolemanTheme.DANGER
        bar_col  = GolemanTheme.DANGER
        label    = "Error"
        lbl_col  = GolemanTheme.DANGER

    return f"""
    <div style="display:flex;align-items:center;gap:10px;padding:10px 12px;
                border-radius:8px;background:{GolemanTheme.BG};
                border:0.5px solid {GolemanTheme.BORDER};margin-bottom:8px">
      <div style="width:30px;height:30px;border-radius:8px;background:{icon_bg};
                  display:flex;align-items:center;justify-content:center;flex-shrink:0">
        <i class="ti {icon}" style="font-size:15px;color:{icon_col}"></i>
      </div>
      <div style="flex:1;min-width:0">
        <div style="font-size:12px;font-weight:500;color:{GolemanTheme.TEXT};
                    white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{filename}</div>
        <div style="font-size:10px;color:{GolemanTheme.MUTED};margin-top:2px">{subtitle}</div>
        <div style="height:4px;background:{GolemanTheme.BORDER};border-radius:2px;
                    margin-top:5px;overflow:hidden">
          <div style="height:100%;border-radius:2px;background:{bar_col};width:100%"></div>
        </div>
      </div>
      <span style="font-size:10px;font-weight:500;color:{lbl_col};flex-shrink:0">{label}</span>
    </div>"""


# ─────────────────────────────────────────────────────────────────────────────
# Sección: strip de estado
# ─────────────────────────────────────────────────────────────────────────────

def _render_status_strip():
    STATUS_ITEMS = [
        ("Legalizaciones",    "legalizations_df"),
        ("Fact. Electr\u00f3nica", "electronic_billing_df"),
        ("RIPS",              "rips_df"),
        ("Facturadores",      "billers_df"),
    ]
    cols = st.columns(4)
    for i, (label, key) in enumerate(STATUS_ITEMS):
        df = st.session_state.get(key)
        has_data = df is not None and not df.empty
        count    = f"{len(df):,}" if has_data else None

        if has_data:
            accent = GolemanTheme.SUCCESS
            dot    = GolemanTheme.SUCCESS
            val_html = f"<div style='font-size:16px;font-weight:500;color:{GolemanTheme.NAVY};margin-top:1px'>{count}</div>"
        elif key == "billers_df":
            accent = GolemanTheme.ORANGE
            dot    = GolemanTheme.ORANGE
            val_html = f"<div style='font-size:13px;color:{GolemanTheme.MUTED};margin-top:1px'>Pendiente</div>"
        else:
            accent = GolemanTheme.BORDER
            dot    = GolemanTheme.BORDER
            val_html = f"<div style='font-size:13px;color:{GolemanTheme.MUTED};margin-top:1px'>Sin datos</div>"

        with cols[i]:
            st.markdown(f"""
            <div style="background:{GolemanTheme.WHITE};border:0.5px solid {GolemanTheme.BORDER};
                        border-left:3px solid {accent};border-radius:10px;padding:11px 14px;
                        display:flex;align-items:center;gap:10px">
              <div style="width:8px;height:8px;border-radius:50%;
                          background:{dot};flex-shrink:0"></div>
              <div style="min-width:0">
                <div style="font-size:11px;font-weight:500;color:{GolemanTheme.TEXT};
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{label}</div>
                {val_html}
              </div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Sección: zonas de carga
# ─────────────────────────────────────────────────────────────────────────────

def _reload_dataset(key: str) -> None:
    api = DataApi()
    try:
        result = api.load_dataset(key)
        if result.get("data"):
            st.session_state[key] = pd.DataFrame(result["data"])
            st.session_state["ultima_actualizacion"] = pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
        else:
            st.session_state[key] = None
    except Exception as e:
        show_error_message(f"Error al recargar datos: {e}")


def _reload_all_datasets() -> None:
    api = DataApi()
    with st.spinner("Recargando todos los datasets..."):
        try:
            result = api.load(include_data=True)
        except Exception as e:
            show_error_message(f"Error al recargar datos: {e}")
            return

    _keys = ("legalizations_df", "rips_df", "billers_df",
             "electronic_billing_df", "administrative_processes_df")
    loaded = 0
    for key in _keys:
        entry = result.get(key)
        if entry and entry.get("data"):
            st.session_state[key] = pd.DataFrame(entry["data"])
            loaded += 1
        else:
            st.session_state[key] = None

    st.session_state["ultima_actualizacion"] = pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
    show_success_message(f"{loaded} datasets recargados.")


def _render_upload_zone(file_cfg: dict):
    key      = file_cfg["key"]
    label    = file_cfg["label"]
    hint     = file_cfg["hint"]
    optional = file_cfg.get("optional", False)

    df_actual = st.session_state.get(key)
    loaded    = df_actual is not None and not df_actual.empty

    chip = _status_chip(loaded, optional)
    warn_msg = ""
    if key == "billers_df" and not loaded:
        warn_msg = (
            f"<div style='font-size:11px;color:{GolemanTheme.WARNING};"
            f"margin-top:4px;display:flex;align-items:center;gap:4px'>"
            f"Sin este archivo los cruces de nombres pueden fallar.</div>"
        )

    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
                margin-bottom:6px">
      <span style="font-size:12px;font-weight:500;color:{GolemanTheme.TEXT}">{label}</span>
      {chip}
    </div>
    <div style="font-size:11px;color:{GolemanTheme.MUTED};margin-bottom:6px">{hint}</div>
    {warn_msg}
    """, unsafe_allow_html=True)

    if key == "billers_df":
        if st.button("\u21bb Recargar Facturadores", key="btn_reload_fact", use_container_width=True):
            with st.spinner("Recargando facturadores..."):
                try:
                    _reload_dataset("billers_df")
                    show_success_message("Facturadores recargados correctamente.")
                    st.rerun()
                except Exception:
                    show_error_message("No se pudo cargar el archivo de facturadores.")
        return

    uploaded = st.file_uploader(
        label,
        type=["xlsx", "xls", "csv"],
        key=f"uploader_{key}",
        label_visibility="collapsed",
    )

    if uploaded is not None:
        file_fingerprint = f"{uploaded.name}_{uploaded.size}"
        last_processed = st.session_state.get(f"_last_processed_{key}")
        if file_fingerprint == last_processed:
            pass
        else:
            upload_ok = False
            with st.spinner(f"Procesando {uploaded.name}\u2026"):
                try:
                    api = DataApi()
                    file_bytes = uploaded.getvalue()

                    if key == "billers_df":
                        result = api.upload_billers(file_bytes, uploaded.name)
                    else:
                        result = api.upload(file_bytes, uploaded.name, key)

                    records = result.get("records", 0)
                    if records > 0:
                        _reload_dataset(key)
                        show_success_message(
                            f"{uploaded.name} cargado \u2014 {records:,} registros."
                        )
                        upload_ok = True
                    else:
                        show_warning_message("El archivo no contiene datos v\u00e1lidos.")

                except Exception as e:
                    detail = str(e)
                    if hasattr(e, "response") and e.response is not None:
                        try:
                            detail = e.response.json().get("detail", detail)
                        except Exception:
                            pass
                    show_error_message(f"Error al procesar {uploaded.name}: {detail}")

            if upload_ok:
                st.session_state[f"_last_processed_{key}"] = file_fingerprint
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Sección: historial de procesamiento
# ─────────────────────────────────────────────────────────────────────────────

def _render_history():
    log = st.session_state.get("upload_log", [])
    if not log:
        st.markdown(
            f"<div style='font-size:12px;color:{GolemanTheme.MUTED};"
            f"padding:16px;text-align:center'>Sin cargas registradas en esta sesi\u00f3n.</div>",
            unsafe_allow_html=True,
        )
        return

    html = ""
    for entry in reversed(log[-10:]):
        html += _progress_item(
            filename=entry["filename"],
            subtitle=f"{entry.get('records', 0):,} registros \u00b7 {entry.get('module','')} \u00b7 {entry.get('time','')}",
            kind=entry.get("status", "ok"),
        )
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Sección: limpieza de datos
# ─────────────────────────────────────────────────────────────────────────────

def _render_clear_data():
    st.markdown(
        GolemanTheme.section_header(
            "Limpiar datos",
            "Elimina los datos cargados de forma permanente.",
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        GolemanTheme.info_banner(
            "Esta acci\u00f3n eliminar\u00e1 los datos cargados de forma permanente.",
            kind="warning",
        ),
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("\u2716 Limpiar Legalizaciones", key="btn_clear_leg", use_container_width=True):
            _clear_data_type(["legalizations_df"], "Legalizaciones", "Legalizaciones")
    with col2:
        if st.button("\u2716 Limpiar Fact. Electr\u00f3nica", key="btn_clear_fact_elec", use_container_width=True):
            _clear_data_type(["electronic_billing_df"], "FacturacionElectronica", "Facturaci\u00f3n Electr\u00f3nica")

    col3, col4 = st.columns(2)
    with col3:
        if st.button("\u2716 Limpiar RIPS", key="btn_clear_rips", use_container_width=True):
            _clear_data_type(["rips_df"], "Rips", "RIPS")
    with col4:
        pass

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("\u2716 LIMPIAR TODOS LOS DATOS", key="btn_clear_all", type="primary", use_container_width=True):
        _clear_all_data()


def _clear_data_type(session_keys, file_key, nombre):
    for key in session_keys:
        if key in st.session_state:
            st.session_state[key] = None

    try:
        DataApi().delete(file_key)
    except Exception as e:
        show_error_message(f"Error al eliminar archivo: {e}")
        return

    show_success_message(f"{nombre} limpiados correctamente.")
    st.rerun()


def _clear_all_data():
    keys_to_clear = [
        "legalizations_df",
        "billing_df",
        "billers_df",
        "electronic_billing_df",
        "administrative_processes_df",
        "rips_df",
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            st.session_state[key] = None

    files_to_delete = ["Legalizaciones", "Facturacion", "FacturacionElectronica", "ArchivoProcesos", "Rips"]
    for file_key in files_to_delete:
        try:
            DataApi().delete(file_key)
        except Exception:
            pass

    show_success_message("Todos los datos han sido limpiados correctamente.")
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Punto de entrada
# ─────────────────────────────────────────────────────────────────────────────

def render_file_upload_section():

    # ── Topbar ───────────────────────────────────────────────────────────────
    c_title, c_btns = st.columns([3, 1])
    with c_title:
        st.markdown(
            GolemanTheme.section_header(
                "Cargar archivos",
                "Sube los archivos Excel de cada m\u00f3dulo. Los datos anteriores se reemplazan.",
            ),
            unsafe_allow_html=True,
        )
    with c_btns:
        if st.button(
            "Recargar todos",
            use_container_width=True,
            type="primary",
            key="btn_reload_all",
        ):
            _reload_all_datasets()

    # ── Strip de estado ──────────────────────────────────────────────────────
    _render_status_strip()
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── Cards por sección – cada upload en su propia fila ────────────────────
    for section_cfg in _UPLOAD_MODULES:
        with st.expander(
            f"{section_cfg['section']}  \u00b7  {section_cfg['hint']}",
            expanded=True,
        ):
            for file_cfg in section_cfg["files"]:
                _render_upload_zone(file_cfg)

    # ── Limpieza de datos ────────────────────────────────────────────────────
    with st.expander("\u26a0 Limpiar datos", expanded=False):
        _render_clear_data()

    # ── Historial ────────────────────────────────────────────────────────────
    with st.expander("Estado de procesamiento", expanded=True):
        _render_history()
