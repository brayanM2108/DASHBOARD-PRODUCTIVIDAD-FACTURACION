"""
Visualizaciones y gráficos
===========================
Funciones para crear gráficos con Plotly y Matplotlib.
"""

import streamlit as st
import plotly.express as px
import pandas as pd


def plot_bar_chart(df, x_col, y_col, title, color=None, sortable=True, sort_key=None):
    """
    Crea un gráfico de barras con Plotly.

    Args:
        df (pd.DataFrame): DataFrame con los datos
        x_col (str): Columna para el eje X
        y_col (str): Columna para el eje Y
        title (str): Título del gráfico
        color (str): Columna para colorear (opcional)
        sortable (bool): Si True, muestra opciones de ordenamiento
        sort_key (str): Clave única para los widgets de ordenamiento
    """
    if df is None or df.empty:
        st.info("No hay datos para graficar.")
        return

    # Crear copia del dataframe
    df_plot = df.copy()

    # Opción de ordenamiento
    if sortable:
        col1, col2 = st.columns([3, 1])
        with col2:
            sort_key_suffix = f"_{sort_key}" if sort_key else ""
            orden = st.selectbox(
                "Ordenar por:",
                options=["Sin ordenar", "Mayor a Menor", "Menor a Mayor"],
                key=f"sort_bar{sort_key_suffix}"
            )

            if orden == "Mayor a Menor":
                df_plot = df_plot.sort_values(by=y_col, ascending=False)
            elif orden == "Menor a Mayor":
                df_plot = df_plot.sort_values(by=y_col, ascending=True)

    # Asegurar que la columna X se trate como texto (categoría) para evitar
    # que valores numéricos se muestren como decimales en el eje X
    df_plot[x_col] = df_plot[x_col].astype(str)

    fig = px.bar(
        df_plot,
        x=x_col,
        y=y_col,
        title=title,
        color=color,
        text=y_col
    )

    fig.update_traces(textposition='outside')
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=True if color else False,
        xaxis_type='category'
    )

    st.plotly_chart(fig, use_container_width="stretch")


def plot_line_chart(df, x_col, y_col, title, color=None, sortable=True, sort_key=None):
    """
    Crea un gráfico de líneas con Plotly.

    Args:
        df (pd.DataFrame): DataFrame con los datos
        x_col (str): Columna para el eje X
        y_col (str): Columna para el eje Y
        title (str): Título del gráfico
        color (str): Columna para colorear (opcional)
        sortable (bool): Si True, muestra opciones de ordenamiento
        sort_key (str): Clave única para los widgets de ordenamiento
    """
    if df is None or df.empty:
        st.info("No hay datos para graficar.")
        return

    # Crear copia del dataframe
    df_plot = df.copy()

    # Opción de ordenamiento
    if sortable:
        col1, col2 = st.columns([3, 1])
        with col2:
            sort_key_suffix = f"_{sort_key}" if sort_key else ""
            orden = st.selectbox(
                "Ordenar por:",
                options=["Por Fecha", "Mayor a Menor", "Menor a Mayor"],
                key=f"sort_line{sort_key_suffix}"
            )

            if orden == "Mayor a Menor":
                df_plot = df_plot.sort_values(by=y_col, ascending=False)
            elif orden == "Menor a Mayor":
                df_plot = df_plot.sort_values(by=y_col, ascending=True)
            else:  # Por Fecha
                df_plot = df_plot.sort_values(by=x_col)

    fig = px.line(
        df_plot,
        x=x_col,
        y=y_col,
        title=title,
        color=color,
        markers=True
    )

    fig.update_layout(xaxis_tickangle=-45)

    st.plotly_chart(fig, use_container_width="stretch")


def plot_metrics_summary(metricas):
    """
    Muestra un resumen de métricas en tarjetas.

    Args:
        metricas (dict): Diccionario con métricas
            Debe contener: 'total', 'promedio_diario'
    """
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Registros", f"{metricas.get('total', 0):,}")

    with col2:
        promedio = metricas.get('promedio_diario', 0)
        st.metric("Promedio Diario", f"{promedio:.2f}")


def plot_productivity_charts(metricas, tipo="Productividad"):
    """
    Muestra gráficos de productividad (por usuario y por fecha).

    Args:
        metricas (dict): Diccionario con métricas calculadas
        tipo (str): Tipo de datos ("PPL", "Convenios", "RIPS", etc.)
    """
    st.subheader(f"📊 Análisis de {tipo}")

    # Métricas generales
    plot_metrics_summary(metricas)

    # Gráfico por usuario
    if metricas.get('por_usuario') is not None and not metricas['por_usuario'].empty:
        st.markdown("### Por Usuario")
        plot_bar_chart(
            metricas['por_usuario'],
            x_col=metricas['por_usuario'].columns[0],  # Primera columna (usuario)
            y_col='CANTIDAD',
            title=f"{tipo} por Usuario",
            sortable=True,
            sort_key=f"{tipo}_usuario"
        )

    # Gráfico por fecha
    if metricas.get('por_fecha') is not None and not metricas['por_fecha'].empty:
        st.markdown("### Por Fecha")
        plot_line_chart(
            metricas['por_fecha'],
            x_col='FECHA',
            y_col='CANTIDAD',
            title=f"{tipo} por Fecha",
            sortable=True,
            sort_key=f"{tipo}_fecha"
        )
