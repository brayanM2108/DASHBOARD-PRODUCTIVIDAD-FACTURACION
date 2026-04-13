"""
Sidebar panel
===========================
Side panel with data status and useful functions.
"""

import streamlit as st
import pandas as  pd
from data.loaders import load_all_persisted_frames

def _show_data_status():
    """It displays the status of the loaded data with visual indicators."""

    datos_estado = [
        ('PPL', 'ppl_legalizations_df'),
        ('Convenios', 'agreement_legalizations_df'),
        ('Fact. Electrónica', 'electronic_billing_df'),
        ('RIPS', 'rips_df'),
        ('Procesos', 'administrative_processes_df'),
        ('Facturadores', 'billers_df')
    ]

    for nombre, key in datos_estado:
        df = st.session_state.get(key)

        if df is not None and not df.empty:
            st.success(f"✅ {nombre}: {len(df)} registros")
        else:
            st.warning(f"⚠️ {nombre}: Sin datos")


def render_state_data():
    """Side panel with data status and useful functions."""

    with st.sidebar:
        st.header("📊 Estado de Datos")

        _show_data_status()

        st.divider()
        _show_quick_summary()

        st.divider()
        _show_quick_actions()

        st.divider()
        _show_last_update()


def _show_quick_summary():
    """Display quick summary metrics."""
    st.subheader("📈 Resumen Rápido")

    df_ppl = st.session_state.get('ppl_legalizations_df')
    df_convenios = st.session_state.get('agreement_legalizations_df')
    df_rips = st.session_state.get('rips_df')
    df_procesos = st.session_state.get('administrative_processes_df')
    total_legalizaciones = 0
    if df_ppl is not None:
        total_legalizaciones += len(df_ppl)
    if df_convenios is not None:
        total_legalizaciones += len(df_convenios)

    st.metric("Total Legalizaciones", total_legalizaciones)

    if df_procesos is not None:
        st.metric("Total Procesos", len(df_procesos))


def _show_quick_actions():
    """Botones de acciones rápidas."""
    st.subheader("⚡ Acciones Rápidas")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Recargar", help="Recarga todos los datos"):
            _reload_data()

    with col2:
        if st.button("🗑️ Limpiar", help="Limpia todos los datos"):
            _clear_data()

def _show_last_update():
    """Display last data update timestamp."""
    st.subheader("🕐 Última Actualización")

    ultima = st.session_state.get('ultima_actualizacion')
    if ultima:
        st.caption(f"📅 {ultima}")
    else:
        st.caption("Sin información")


def _reload_data():
    """Reload persisted datasets into session state."""


    data = load_all_persisted_frames()
    st.session_state["ppl_legalizations_df"] = data.get("ppl_legalizations")
    st.session_state["agreement_legalizations_df"] = data.get("agreement_legalizations")
    st.session_state["electronic_billing_df"] = data.get("electronic_billing"),
    st.session_state["rips_df"] = data.get("rips")
    st.session_state["billers_df"] = data.get("billers")
    st.session_state["administrative_processes_df"] = data.get("administrative_processes")
    st.session_state['ultima_actualizacion'] = pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
    st.rerun()


def _clear_data():
    """Clear session-state datasets."""
    keys = [
        'ppl_legalizations_df',
        'agreement_legalizations_df',
        'rips_df',
        'billers_df',
        'electronic_billing_df',
        'administrative_processes_df',
    ]
    for key in keys:
        st.session_state[key] = None
    st.rerun()