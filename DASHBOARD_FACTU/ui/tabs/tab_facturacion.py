"""
Pestaña de Facturación
=======================
Interfaz para visualizar y analizar facturación.
"""

import streamlit as st
import pandas as pd

from service.facturador_service import (
    filtrar_facturacion,
    calcular_productividad_facturacion,
    obtener_facturacion_con_usuario
)
from ui.visualizations import plot_productivity_charts, plot_bar_chart
from ui.components import show_dataframe, create_download_button, show_info_message
from data.validators import find_column_variant
from config.settings import COLUMN_NAMES

def render_tab_facturacion():
    """
    Renderiza la pestaña de facturación.

    Args:
        filtros (dict): Filtros aplicados (start_date, end_date, usuarios_seleccionados)
    """
    st.header("Facturación")


    render_facturacion_section()


def render_facturacion_section():
    """Renderiza la sección de facturación con filtros independientes."""

    df_facturacion = st.session_state.get('df_facturacion')
    df_facturadores = st.session_state.get('df_facturadores')
    df_fact_elec = st.session_state.get('df_facturacion_electronica')

    if df_facturacion is None or df_facturacion.empty:
        show_info_message("No hay datos de facturación. Carga un archivo en la sección de carga.")
        return

    # Encontrar columna de fecha
    fecha_col = find_column_variant(df_facturacion, COLUMN_NAMES["fecha"])

    # Filtros independientes para Facturación
    col1, col2 = st.columns(2)
    with col1:
        try:
            if fecha_col and fecha_col in df_facturacion.columns:
                fecha_min = pd.to_datetime(df_facturacion[fecha_col]).min()
            else:
                fecha_min = pd.Timestamp.now()
            if pd.isna(fecha_min):
                fecha_min = pd.Timestamp.now()
        except:
            fecha_min = pd.Timestamp.now()
        fecha_inicio = st.date_input("Fecha inicio", value=fecha_min, key="facturacion_fecha_inicio")

    with col2:
        try:
            if fecha_col and fecha_col in df_facturacion.columns:
                fecha_max = pd.to_datetime(df_facturacion[fecha_col]).max()
            else:
                fecha_max = pd.Timestamp.now()
            if pd.isna(fecha_max):
                fecha_max = pd.Timestamp.now()
        except:
            fecha_max = pd.Timestamp.now()
        fecha_fin = st.date_input("Fecha fin", value=fecha_max, key="facturacion_fecha_fin")

    # Obtener lista de usuarios desde facturación electrónica
    usuarios_lista = ['Todos']
    if df_fact_elec is not None and not df_fact_elec.empty:
        usuario_col_elec = find_column_variant(df_fact_elec, COLUMN_NAMES["usuario"])
        if usuario_col_elec and usuario_col_elec in df_fact_elec.columns:
            usuarios_unicos = df_fact_elec[usuario_col_elec].dropna().unique().tolist()
            usuarios_lista = ['Todos'] + sorted(usuarios_unicos)

    usuario_sel = st.selectbox("Usuario", usuarios_lista, key="facturacion_usuario")
    usuarios_seleccionados = None if usuario_sel == 'Todos' else [usuario_sel]

    # Aplicar filtros de fecha
    df_filtered = filtrar_facturacion(
        df_facturacion,
        fecha_inicio,
        fecha_fin,
        usuarios_seleccionados=None
    )

    if df_filtered is None or df_filtered.empty:
        show_info_message("No hay datos que coincidan con los filtros seleccionados.")
        return

    st.subheader("📈 Facturación por Usuario")

    # Obtener facturación con usuario desde el servicio
    resultado = obtener_facturacion_con_usuario(df_filtered, df_fact_elec, df_facturadores)

    if resultado["error"]:
        st.warning(resultado["error"])
    else:
        df_por_usuario = resultado["df_por_usuario"]
        usuario_col = resultado["usuario_col"]

        # Aplicar filtro de usuario si se seleccionó uno específico
        if usuarios_seleccionados:
            df_por_usuario = df_por_usuario[
                df_por_usuario[usuario_col].isin(usuarios_seleccionados)
            ]

        if not df_por_usuario.empty:
            nombre_col = 'NOMBRE' if 'NOMBRE' in df_por_usuario.columns else usuario_col

            plot_bar_chart(
                df_por_usuario,
                x_col=nombre_col,
                y_col='CANTIDAD',
                title="Facturación por Usuario"
            )
            st.dataframe(df_por_usuario, use_container_width="stretch")

    # Calcular métricas
    metricas = calcular_productividad_facturacion(df_filtered)

    # Mostrar gráficos
    plot_productivity_charts(metricas, tipo="Facturación")

    # Mostrar tabla de datos
    with st.expander("📊 Ver datos detallados", expanded=False):
        show_dataframe(df_filtered, title="Datos de Facturación")
        create_download_button(df_filtered, "facturacion.csv")
