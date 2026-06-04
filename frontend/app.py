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
from frontend.components.sidebar import render_state_data
from frontend.pages.tab_legalizations import render_tab_legalizations
from frontend.pages.tab_manual_billing import render_tab_manual_billing
from frontend.pages.tab_billing_electronic import render_billing_electronic_section


from frontend.pages.login_page import render_login_page
from frontend.auth.auth_guard import is_authenticated


GOLEMAN_CSS = """
<style>
:root {
  --g-navy: #0D2B5E;
  --g-blue: #1565C0;
  --g-blue-light: #E8F0FB;
  --g-orange: #F57C00;
  --g-orange-light: #FEF3E6;
  --g-bg: #F5F7FA;
  --g-border: #D0DAE8;
  --g-text: #1A2A45;
  --g-muted: #5A6A84;
  --g-success-bg: #E6F4EA;
  --g-success: #2E7D32;
}

[data-testid="stAppViewContainer"] { background: var(--g-bg); }
[data-testid="stHeader"] { background: var(--g-navy) !important; }
[data-testid="stSidebar"] {
  background: var(--g-navy) !important;
  border-right: none;
}
[data-testid="stSidebar"] * { color: rgba(255,255,255,.85) !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.12) !important; }

[data-testid="stTabs"] [role="tablist"] {
  background: var(--g-navy);
  padding: 0 8px;
  border-radius: 0;
  gap: 0;
}
[data-testid="stTabs"] button[role="tab"] {
  color: rgba(255,255,255,.55);
  border-bottom: 2px solid transparent;
  border-radius: 0;
  padding: 10px 16px;
  font-size: 13px;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
  color: #fff !important;
  border-bottom-color: var(--g-orange) !important;
  background: transparent !important;
}

[data-testid="stMetric"] {
  background: #fff;
  border-radius: 10px;
  border: 0.5px solid var(--g-border);
  padding: 14px 16px;
  border-left: 3px solid var(--g-orange);
}
[data-testid="stMetricLabel"] p { color: var(--g-muted) !important; font-size: 11px; }
[data-testid="stMetricValue"] { color: var(--g-navy) !important; font-size: 22px; font-weight: 500; }

[data-testid="stButton"] > button {
  background: var(--g-blue) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 500;
}
[data-testid="stButton"] > button:hover { background: var(--g-navy) !important; }
[data-testid="stDownloadButton"] > button {
  background: transparent !important;
  color: var(--g-orange) !important;
  border: 1.5px solid var(--g-orange) !important;
  border-radius: 8px !important;
  font-weight: 500;
}
[data-testid="stDownloadButton"] > button:hover { background: var(--g-orange-light) !important; }

h1, h2, h3 { color: var(--g-navy) !important; }
h3 { border-left: 3px solid var(--g-orange); padding-left: 10px; }

[data-testid="stDataFrame"] thead th {
  background: var(--g-navy) !important;
  color: #fff !important;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: .04em;
}
[data-testid="stDataFrame"] tbody tr:hover td { background: var(--g-blue-light) !important; }

[data-testid="stAlert"][data-baseweb="notification"] {
  border-radius: 10px;
  border-left: 3px solid var(--g-blue);
}
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stDateInput"] input {
  border-color: var(--g-border) !important;
  border-radius: 8px !important;
  background: #fff !important;
}

.g-tab-header {
  background: var(--g-navy);
  border-radius: 12px 12px 0 0;
  padding: 16px 24px;
  color: #fff;
  border: 0.5px solid var(--g-border);
  border-bottom: none;
}
.g-tab-header-title {
  color: #fff;
  font-size: 15px;
  font-weight: 500;
}
.g-tab-header-title span { color: var(--g-orange); margin-right: 8px; }
.g-section {
  background: #fff;
  border-left: 0.5px solid var(--g-border);
  border-right: 0.5px solid var(--g-border);
  border-bottom: 0.5px solid var(--g-border);
  padding: 18px 24px;
}
.g-section-title {
  color: var(--g-blue);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: .05em;
  text-transform: uppercase;
  margin-bottom: 12px;
}
.g-chart-card {
  background: #fff;
  border-radius: 10px;
  border: 0.5px solid var(--g-border);
  padding: 16px;
}
.g-table-card {
  background: #fff;
  border-radius: 10px;
  border: 0.5px solid var(--g-border);
  padding: 12px 16px 16px;
}
.g-muted-note {
  color: var(--g-muted);
  font-size: 11px;
}
</style>
"""


def init_session_state():

    if 'initialized' not in st.session_state:
        data = load_all_persisted_frames_cached()


        st.session_state["ppl_legalizations_df"] = data.get("ppl_legalizations")
        st.session_state["agreement_legalizations_df"] = data.get("agreement_legalizations")
        st.session_state["billers_df"] = data.get("billers")
        st.session_state["electronic_billing_df"] = data.get("electronic_billing")
        st.session_state["administrative_processes_df"] = data.get("administrative_processes")

        if st.session_state["billers_df"] is None:
            st.session_state["billers_df"] = load_billers_master_cached()

        st.session_state["initialized"] = True


def main():

    st.set_page_config(**PAGE_CONFIG)
    st.markdown(GOLEMAN_CSS, unsafe_allow_html=True)

    if not is_authenticated():

        render_login_page()

        st.stop()

    init_session_state()

    col1, col2 = st.columns([1,5])

    with col1:
        st.image("assets/LOGO_OSCURO.svg", width=100)

    with col2:
        st.title("Dashboard de Productividad")

    render_state_data()

    tab_home, tab_legalizations, tab_electronic_billing, tab_manual_billing, tab_load = st.tabs([
        "🏠 Inicio",
        "📋 Legalizaciones",
        "💰 Facturación",
        "🔧 Procesos Administrativos",
        "📂 Cargar Archivos"
    ])

    with tab_home:
        render_home()

    with tab_legalizations:
        render_tab_legalizations()

    with tab_electronic_billing:
        render_billing_electronic_section()

    with tab_manual_billing:
        render_tab_manual_billing()

    with tab_load:
        render_file_upload_section()


def render_home():

    st.header("🏠 Resumen General")

    st.subheader("📁 Estado de Datos")

    col1, col2, col3 = st.columns(3)

    with col1:
        df_ppl = st.session_state.get('ppl_legalizations_df')
        count_ppl = len(df_ppl) if df_ppl is not None else 0
        st.metric("Legalizaciones PPL", count_ppl)
        df_convenios = st.session_state.get('agreement_legalizations_df')
        count_conv = len(df_convenios) if df_convenios is not None else 0
        st.metric("Legalizaciones Convenios", count_conv)

        df_facturadores = st.session_state.get('billers_df')
        count_fact = len(df_facturadores) if df_facturadores is not None else 0
        st.metric("Facturadores", count_fact)

    with col2:
        df_fact_elec = st.session_state.get('electronic_billing_df')
        count_fact_elec = len(df_fact_elec) if df_fact_elec is not None else 0
        st.metric("Facturación Electrónica", count_fact_elec)

    with col3:
        df_procesos = st.session_state.get('administrative_processes_df')
        count_procesos = len(df_procesos) if df_procesos is not None else 0
        st.metric("Procesos Administrativos", count_procesos)

        if df_procesos is not None and not df_procesos.empty:
            total_cantidad = df_procesos['CANTIDAD'].sum() if 'CANTIDAD' in df_procesos.columns else 0

            try:
                total_cantidad = float(total_cantidad)
                st.metric("Total Cantidad Procesos", f"{total_cantidad:,.0f}")
            except (ValueError, TypeError):
                st.metric("Total Cantidad Procesos", "N/A")

    st.markdown("---")
    st.subheader("📖 Instrucciones")
    st.markdown("""
    1. **Cargar Archivos**: Ve a la pestaña "📂 Cargar Archivos" para subir tus datos.
    2. **Filtrar**: Usa la barra lateral para filtrar por fechas y facturadores.
    3. **Analizar**: Navega por las pestañas para ver métricas y gráficos.
    4. **Exportar**: Descarga los informes en formato Excel.
    """)


if __name__ == "__main__":
    main()
