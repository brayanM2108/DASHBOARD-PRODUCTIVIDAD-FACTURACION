"""
Dashboard de Productividad - Legalización y Facturación
========================================================

Este módulo implementa un dashboard interactivo en Streamlit para el análisis de productividad
en procesos de legalización y facturación de servicios de salud.

Características principales:
- Carga y procesamiento de archivos Excel/CSV con detección automática de encabezados
- Gestión persistente de datos mediante archivos Parquet
- Filtrado dinámico por tipo de legalización, usuario y rango de fechas
- Visualizaciones comparativas y evolutivas de productividad
- Integración de facturación con facturación electrónica mediante búsqueda de usuarios
- Descarga de reportes procesados

Estructura de datos:
- PPL: Legalizaciones del Patrimonio Autónomo Fondo Atención Salud PPL 2024
- Convenios: Legalizaciones de otros convenios
- RIPS: Registros Individuales de Prestación de Servicios de Salud
- Facturación: Datos de facturación general
- Facturación Electrónica: Mapeo de facturas a usuarios

Autor: Brayan Melo
Versión: 1.0
"""

from io import BytesIO
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import os

# --- Configuración de la página ---
# Establece el título, ícono y diseño de la página de Streamlit
st.set_page_config(page_title="Dashboard de Productividad", page_icon="📊", layout="wide")

# Directorio para almacenamiento persistente de datos procesados
PERSISTED_DATA_DIR = "persisted_data"
os.makedirs(PERSISTED_DATA_DIR, exist_ok=True)

# Archivo maestro de facturadores (debe estar en el directorio del proyecto)
FACTURADORES_FILE = "FACTURADORES.xlsx"

# Nombre o índice de la hoja donde están los facturadores (0 = primera hoja, 1 = segunda, etc.)
# También puedes usar el nombre de la hoja, por ejemplo: "Hoja1", "Facturadores", etc.
FACTURADORES_SHEET = 1

# Diccionario con las rutas de los archivos Parquet para cada tipo de dato
FILES = {
    "PPL": os.path.join(PERSISTED_DATA_DIR, "df_ppl.parquet"),
    "Convenios": os.path.join(PERSISTED_DATA_DIR, "df_convenios.parquet"),
    "RIPS": os.path.join(PERSISTED_DATA_DIR, "df_rips.parquet"),
    "Facturacion": os.path.join(PERSISTED_DATA_DIR, "df_facturacion.parquet"),
    "Facturadores": os.path.join(PERSISTED_DATA_DIR, "df_facturadores.parquet")
}


# --- FUNCIONES DE CARGA ---
def save_local(df, filepath):
    """
    Guarda un DataFrame localmente en formato Parquet.

    Convierte todas las columnas a string antes de guardar para evitar
    problemas de compatibilidad de tipos de datos.

    Args:
        df (pd.DataFrame): DataFrame a guardar. Puede ser None o vacío.
        filepath (str): Ruta completa del archivo donde se guardará el DataFrame.

    Returns:
        None
    Nota:
        Si el DataFrame es None o está vacío, no se realiza ninguna acción.
    """
    if df is not None and not df.empty:
        df.astype(str).to_parquet(filepath, index=False)


def load_local(filepath):
    """
    Carga un DataFrame desde un archivo Parquet local.

    Args:
        filepath (str): Ruta completa del archivo Parquet a cargar.

    Returns:
        pd.DataFrame or None: El DataFrame cargado si el archivo existe,
                             None en caso contrario.
    """
    return pd.read_parquet(filepath) if os.path.exists(filepath) else None


def cargar_facturadores_desde_local():
    """
    Carga el archivo maestro de facturadores desde el disco local.

    Busca el archivo FACTURADORES.xlsx en el directorio del proyecto y lo carga.
    Si no existe, intenta cargar desde el Parquet persistido.
    Si ya está procesado y guardado en Parquet, lo carga de ahí.

    Returns:
        pd.DataFrame or None: DataFrame con columnas DOCUMENTO y NOMBRE,
                             None si no existe el archivo.
    """
    # SIEMPRE cargar desde Excel para garantizar datos actualizados
    if os.path.exists(FACTURADORES_FILE):
        try:
            # Cargar desde la hoja especificada
            df = pd.read_excel(FACTURADORES_FILE, sheet_name=FACTURADORES_SHEET)

            # Normalizar nombres de columnas
            df.columns = df.columns.astype(str).str.strip().str.upper()

            # Verificar columnas requeridas
            if 'DOCUMENTO' in df.columns and 'NOMBRE' in df.columns:
                # Eliminar filas donde DOCUMENTO o NOMBRE estén vacíos
                df = df.dropna(subset=['DOCUMENTO', 'NOMBRE'])

                # Convertir DOCUMENTO a string (ya viene como int64 del Excel)
                df['DOCUMENTO'] = df['DOCUMENTO'].astype(str).str.strip()

                # Normalizar NOMBRE
                df['NOMBRE'] = df['NOMBRE'].astype(str).str.strip().str.upper()

                # Filtrar filas con documentos vacíos
                df = df[df['DOCUMENTO'] != '']
                df = df[df['DOCUMENTO'] != 'nan']

                # Guardar en Parquet para referencia
                if not df.empty:
                    save_local(df, FILES["Facturadores"])
                    return df
                else:
                    st.warning(f"⚠️ El archivo {FACTURADORES_FILE} no contiene datos válidos después de limpiar")
                    return None
            else:
                st.warning(f"⚠️ El archivo {FACTURADORES_FILE} no tiene las columnas DOCUMENTO y NOMBRE")
                return None
        except Exception as e:
            st.warning(f"⚠️ No se pudo cargar {FACTURADORES_FILE}: {e}")
            import traceback
            st.error(traceback.format_exc())
            return None

    # Si no existe Excel, intenta cargar desde Parquet (backup)
    if os.path.exists(FILES["Facturadores"]):
        try:
            df = pd.read_parquet(FILES["Facturadores"])
            return df
        except Exception as e:
            st.warning(f"⚠️ Error al cargar Parquet: {e}")
            return None

    return None


def buscar_usuario_en_fact_electronica(df_fact, df_fact_elec):
    """
    Busca y asigna el usuario de facturación electrónica a cada factura.

    Esta función realiza una búsqueda tipo BUSCARX/VLOOKUP entre dos DataFrames:
    - df_fact: Contiene las facturas que necesitan el campo USUARIO
    - df_fact_elec: Contiene el mapeo FACTURA → USUARIO

    Proceso:
    1. Valida que ambos DataFrames existan y no estén vacíos
    2. Normaliza todos los valores de texto a mayúsculas y sin espacios
    3. Filtra solo las facturas electrónicas en estado ACTIVO
    4. Crea un mapeo único FACTURA → USUARIO
    5. Asigna el USUARIO a df_fact mediante la columna NRO_FACTURACLI

    Args:
        df_fact (pd.DataFrame): DataFrame de facturación con columna 'NRO_FACTURACLI'.
                               Se espera que tenga una columna USUARIO vacía o a completar.
        df_fact_elec (pd.DataFrame): DataFrame de facturación electrónica con columnas
                                    'FACTURA', 'USUARIO' y 'Estado'.

    Returns:
        pd.DataFrame: El DataFrame df_fact original con la columna 'USUARIO' actualizada.
                     Si hay facturas sin coincidencia, su USUARIO quedará como NaN.
                     Si alguno de los DataFrames de entrada es None o vacío, retorna df_fact sin cambios.
    """
    if (
            df_fact is None or df_fact.empty or
            df_fact_elec is None or df_fact_elec.empty
    ):
        return df_fact

    # -------- Normalización --------
    # Convierte todos los campos de texto a mayúsculas y elimina espacios
    # para garantizar coincidencias exactas independientemente del formato original
    for df in [df_fact, df_fact_elec]:
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.strip()
                    .str.upper()
                )

    # Filtra solo las facturas electrónicas en estado ACTIVO
    df_fact_elec_activa = df_fact_elec[
        df_fact_elec['Estado'] == 'ACTIVO'
        ]

    # -------- Mapa FACTURA → USUARIO --------
    # Crea un diccionario/Serie donde la clave es el número de factura
    # y el valor es el usuario asociado
    mapa_usuario = (
        df_fact_elec_activa
        .dropna(subset=['FACTURA', 'USUARIO'])
        .drop_duplicates(subset=['FACTURA'])
        .set_index('FACTURA')['USUARIO']
    )

    # -------- BUSCARX --------
    # Asigna el USUARIO a cada registro de df_fact
    df_fact['USUARIO'] = df_fact['NRO_FACTURACLI'].map(mapa_usuario)
    return df_fact


def cruzar_documento_a_nombre(df_rips, df_facturadores):
    """
    Reemplaza el DOCUMENTO del facturador por su NOMBRE en RIPS.

    Esta función realiza un cruce tipo BUSCARX/VLOOKUP:
    - df_rips: Contiene la columna 'USUARIO FACTURÓ' con documentos
    - df_facturadores: Contiene el mapeo DOCUMENTO → NOMBRE

    Proceso:
    1. Valida que ambos DataFrames existan y no estén vacíos
    2. Normaliza documentos (mayúsculas, sin espacios)
    3. Crea mapeo DOCUMENTO → NOMBRE
    4. Reemplaza valores en 'USUARIO FACTURÓ' por el nombre correspondiente

    Args:
        df_rips (pd.DataFrame): DataFrame de RIPS con columna 'USUARIO FACTURÓ'.
        df_facturadores (pd.DataFrame): DataFrame con columnas 'DOCUMENTO' y 'NOMBRE'.

    Returns:
        pd.DataFrame: El DataFrame df_rips con 'USUARIO FACTURÓ' actualizado a nombres.
                     Si no hay coincidencia, mantiene el documento original.
    """
    if df_rips is None or df_rips.empty:
        return df_rips

    if df_facturadores is None or df_facturadores.empty:
        return df_rips

    # Verificar que existan las columnas necesarias
    if 'USUARIO FACTURÓ' not in df_rips.columns:
        return df_rips

    if 'DOCUMENTO' not in df_facturadores.columns or 'NOMBRE' not in df_facturadores.columns:
        return df_rips

    # Normalizar DOCUMENTO en ambos DataFrames
    df_facturadores_norm = df_facturadores.copy()
    df_facturadores_norm['DOCUMENTO'] = (
        df_facturadores_norm['DOCUMENTO']
        .astype(str)
        .str.strip()
        .str.upper()
    )
    df_facturadores_norm['NOMBRE'] = (
        df_facturadores_norm['NOMBRE']
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # Crear mapeo DOCUMENTO → NOMBRE
    mapa_nombre = (
        df_facturadores_norm
        .dropna(subset=['DOCUMENTO', 'NOMBRE'])
        .drop_duplicates(subset=['DOCUMENTO'])
        .set_index('DOCUMENTO')['NOMBRE']
    )

    # Normalizar columna en RIPS
    df_rips['USUARIO FACTURÓ'] = (
        df_rips['USUARIO FACTURÓ']
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # Aplicar cruce: si encuentra el documento, lo reemplaza por el nombre
    df_rips['USUARIO FACTURÓ'] = df_rips['USUARIO FACTURÓ'].map(mapa_nombre).fillna(df_rips['USUARIO FACTURÓ'])

    return df_rips



# --- INICIALIZACIÓN ---
# Carga los datos persistidos al iniciar la aplicación (solo una vez por sesión)
if 'initialized' not in st.session_state:
    st.session_state.df_ppl = load_local(FILES["PPL"])
    st.session_state.df_convenios = load_local(FILES["Convenios"])
    st.session_state.df_rips = load_local(FILES["RIPS"])
    st.session_state.df_facturacion = load_local(FILES["Facturacion"])

    # Cargar facturadores desde archivo local (FACTURADORES.xlsx)
    st.session_state.df_facturadores = cargar_facturadores_desde_local()

    # Aplicar cruce DOCUMENTO → NOMBRE a RIPS si ya hay datos cargados
    if st.session_state.df_rips is not None and st.session_state.df_facturadores is not None:
        st.session_state.df_rips = cruzar_documento_a_nombre(
            st.session_state.df_rips,
            st.session_state.df_facturadores
        )

    st.session_state.df_fact_elec = load_local(
        os.path.join(PERSISTED_DATA_DIR, "df_fact_elec.parquet")
    )

    st.session_state.initialized = True

# --- CARGA DE ARCHIVOS ---
st.title("📥 Carga de Archivos - Legalización, RIPS y Facturación")

# --- INDICADOR DE FACTURADORES ---
st.subheader("👤 Maestro de Facturadores (Archivo Local)")
if st.session_state.df_facturadores is not None and not st.session_state.df_facturadores.empty:
    col_ind1, col_ind2 = st.columns([4, 1])
    with col_ind1:
        st.success(f"✅ Archivo **{FACTURADORES_FILE}** cargado: {len(st.session_state.df_facturadores):,} facturadores")
        st.caption(f"📂 Ubicación: `{os.path.abspath(FACTURADORES_FILE)}`")
    with col_ind2:
        if st.button("🔄 Recargar", key="recargar_facturadores", use_container_width="stretch"):
            st.session_state.df_facturadores = cargar_facturadores_desde_local()
            st.rerun()
else:
    st.warning(f"⚠️ Archivo **{FACTURADORES_FILE}** no encontrado")
    st.info(f"""
    📝 **Instrucciones:**
    1. Crea un archivo Excel llamado `{FACTURADORES_FILE}` en el directorio del proyecto
    2. Asegúrate de que tenga las columnas: **DOCUMENTO** y **NOMBRE**
    3. Guarda el archivo y recarga la aplicación
    
    📂 Ubicación esperada: `{os.path.abspath(FACTURADORES_FILE)}`
    """)

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

# --- Columna 1: Legalizaciones (PPL + Convenios + RIPS) ---
with col1:
    st.subheader("Legalizaciones")

    file1 = st.file_uploader("Sube el archivo de Legalizaciones (PPL + CONVENIOS)", type=["xlsx", "xls", "csv"], key="file1")

    if file1 is not None:
        try:
            # -------- LECTURA ROBUSTA DEL ARCHIVO --------
            # Lee el archivo sin asumir dónde están los encabezados
            if file1.name.endswith('.csv'):
                df_raw = pd.read_csv(file1, header=None)
            else:
                df_raw = pd.read_excel(file1, header=None)

            # Busca la fila que contiene 'ID_LEGALIZACION' para identificar los encabezados
            header_row = None
            for i, row in df_raw.iterrows():
                if row.astype(str).str.strip().str.upper().str.startswith("ID_LEGALIZACION").any():
                    header_row = i
                    break

            if header_row is None:
                st.error("❌ No se encontró la fila de columnas que contiene 'ID_LEGALIZACION'")
                st.stop()

            # Relee el archivo usando la fila identificada como encabezado
            if file1.name.endswith('.csv'):
                df_temp = pd.read_csv(file1, header=header_row)
            else:
                df_temp = pd.read_excel(file1, header=header_row)

            # Limpia los nombres de las columnas (espacios, saltos de línea)
            df_temp.columns = (
                df_temp.columns
                .astype(str)
                .str.strip()
                .str.replace('\n', ' ')
            )
            st.success(f"✅ Archivo cargado: {len(df_temp):,} filas")
            st.info(f"📋 Encabezados detectados en fila: {header_row + 1}")

            # Botón para procesar y separar los datos
            if st.button("💾 Procesar y Guardar Legalizaciones", use_container_width="stretch"):
                try:
                    # -------- FILTRO POR ESTADO --------
                    # Solo incluye LEGALIZACIONES con estado válido (Activa)
                    estados_validos_legalizaciones = ['Activo', 'ACTIVO']

                    if 'ESTADO' in df_temp.columns or 'Estado' in df_temp.columns:
                        # Detecta la columna de estado
                        col_estado = 'ESTADO' if 'ESTADO' in df_temp.columns else 'Estado'

                        # Normaliza los valores de ESTADO a mayúsculas para comparación
                        df_temp[col_estado] = df_temp[col_estado].astype(str).str.strip().str.upper()

                        # Filtra solo registros con estado válido
                        registros_antes = len(df_temp)
                        df_temp = df_temp[df_temp[col_estado].isin(estados_validos_legalizaciones)].copy()
                        registros_despues = len(df_temp)

                        st.info(
                            f"📊 Filtrado por estado: {registros_despues:,} de {registros_antes:,} registros tienen estado válido ({', '.join(estados_validos_legalizaciones)})")

                        if registros_despues == 0:
                            st.warning(
                                "⚠️ No hay registros con estado válido. Verifica los valores de la columna ESTADO en tu archivo.")
                            st.write("**Valores de ESTADO encontrados:**", df_temp[col_estado].unique().tolist())
                            st.stop()
                    else:
                        st.warning(
                            "⚠️ No se encontró la columna 'ESTADO' en el archivo de LEGALIZACIONES. Se procesarán TODOS los registros sin filtrar por estado.")

                    # Verifica que existe la columna CONVENIO
                    if 'CONVENIO' not in df_temp.columns:
                        st.error("❌ No se encontró la columna 'CONVENIO' en el archivo")
                        st.stop()

                    # SEPARACIÓN AUTOMÁTICA basada en el valor del campo CONVENIO:
                    df_ppl = df_temp[df_temp['CONVENIO'] == 'Patrimonio Autonomo Fondo Atención Salud PPL 2024'].copy()
                    df_convenios = df_temp[
                        df_temp['CONVENIO'] != 'Patrimonio Autonomo Fondo Atención Salud PPL 2024'].copy()
                    df_rips = pd.DataFrame()  # Vacío por ahora

                    # Guarda en session_state
                    st.session_state.df_ppl = df_ppl if not df_ppl.empty else None
                    st.session_state.df_convenios = df_convenios if not df_convenios.empty else None
                    st.session_state.df_rips = df_rips if not df_rips.empty else None

                    # Guarda archivos locales en formato Parquet
                    save_local(df_ppl, FILES["PPL"])
                    save_local(df_convenios, FILES["Convenios"])
                    save_local(df_rips, FILES["RIPS"])

                    # Muestra resumen de procesamiento
                    total_procesado = len(df_ppl) + len(df_convenios) + len(df_rips)

                    st.success(f"""✅ Datos procesados y guardados:

**PPL:** {len(df_ppl):,} registros
**Convenios:** {len(df_convenios):,} registros

**Total procesado:** {total_procesado:,} / {len(df_temp):,} filas
                    """)

                    if total_procesado != len(df_temp):
                        st.warning(f"⚠️ Hay {len(df_temp) - total_procesado} registros sin clasificar")

                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error al procesar: {e}")
                    import traceback

                    st.code(traceback.format_exc())

        except Exception as e:
            st.error(f"❌ Error al leer el archivo: {e}")
            import traceback

            st.code(traceback.format_exc())

# --- Columna 2: Legalizaciones (RIPS) ---
with col2:
    st.subheader("RIPS")

    file2 = st.file_uploader("Sube el archivo de RIPS", type=["xlsx", "xls", "csv"], key="file2")

    if file2 is not None:
        try:
            # -------- LECTURA ROBUSTA DEL ARCHIVO --------
            # Lee el archivo sin asumir dónde están los encabezados
            if file2.name.endswith('.csv'):
                df_raw = pd.read_csv(file2, header=None)
            else:
                df_raw = pd.read_excel(file2, header=None)

            # Busca la fila que contiene 'CODIGO' para identificar los encabezados
            header_row = None
            for i, row in df_raw.iterrows():
                if row.astype(str).str.strip().str.upper().str.startswith("CÓDIGO").any():
                    header_row = i
                    break

            if header_row is None:
                st.error("❌ No se encontró la fila de columnas que contiene 'CODIGO'")
                st.stop()

            # Relee el archivo usando la fila identificada como encabezado
            if file2.name.endswith('.csv'):
                df_temp = pd.read_csv(file2, header=header_row)
            else:
                df_temp = pd.read_excel(file2, header=header_row)

            # Limpia los nombres de las columnas (espacios, saltos de línea)
            df_temp.columns = (
                df_temp.columns
                .astype(str)
                .str.strip()
                .str.replace('\n', ' ')
            )
            st.success(f"✅ Archivo cargado: {len(df_temp):,} filas")
            st.info(f"📋 Encabezados detectados en fila: {header_row + 1}")

            # Botón para procesar y separar los datos
            if st.button("💾 Procesar y Guardar RIPS", use_container_width="stretch"):
                try:
                    # -------- FILTRO POR ESTADO --------
                    # Solo incluye RIPS con estado válido (finalizadas/aprobadas)
                    estados_validos_rips = ['Completo', 'COMPLETO']

                    if 'ESTADO' in df_temp.columns or 'Estado' in df_temp.columns:
                        # Detecta la columna de estado
                        col_estado = 'ESTADO' if 'ESTADO' in df_temp.columns else 'Estado'

                        # Normaliza los valores de ESTADO a mayúsculas para comparación
                        df_temp[col_estado] = df_temp[col_estado].astype(str).str.strip().str.upper()

                        # Filtra solo registros con estado válido
                        registros_antes = len(df_temp)
                        df_temp = df_temp[df_temp[col_estado].isin(estados_validos_rips)].copy()
                        registros_despues = len(df_temp)

                        st.info(f"📊 Filtrado por estado: {registros_despues:,} de {registros_antes:,} registros tienen estado válido ({', '.join(estados_validos_rips)})")

                        if registros_despues == 0:
                            st.warning("⚠️ No hay registros con estado válido. Verifica los valores de la columna ESTADO en tu archivo.")
                            st.write("**Valores de ESTADO encontrados:**", df_temp[col_estado].unique().tolist())
                            st.stop()
                    else:
                        st.warning("⚠️ No se encontró la columna 'ESTADO' en el archivo de RIPS. Se procesarán TODOS los registros sin filtrar por estado.")

                    # Asigna df_temp a df_rips
                    df_rips = df_temp.copy()

                    # -------- CRUCE DOCUMENTO → NOMBRE --------
                    # Aplica el cruce con el maestro de facturadores
                    if st.session_state.df_facturadores is not None:
                        df_rips = cruzar_documento_a_nombre(df_rips, st.session_state.df_facturadores)
                        st.info("🔄 Cruce DOCUMENTO → NOMBRE aplicado exitosamente")
                    else:
                        st.warning("⚠️ No hay maestro de facturadores cargado. Los documentos en 'USUARIO FACTURÓ' no se convertirán a nombres.")

                    # Guarda en session_state
                    st.session_state.df_rips = df_rips if not df_rips.empty else None

                    # Guarda archivo local en formato Parquet
                    save_local(df_rips, FILES["RIPS"])

                    # Muestra resumen de procesamiento
                    st.success(f"""✅ Datos procesados y guardados:

**RIPS:** {len(df_rips):,} registros
                    """)

                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error al procesar: {e}")
                    import traceback

                    st.code(traceback.format_exc())

        except Exception as e:
            st.error(f"❌ Error al leer el archivo: {e}")
            import traceback

            st.code(traceback.format_exc())

# --- Columna 3: Facturación ---
with (col3):
    st.subheader("Facturación")

    file3 = st.file_uploader("Sube el archivo de Facturación", type=["xlsx", "xls", "csv"], key="file3")

    if file3 is not None:
        try:
            # -------- LECTURA ROBUSTA DEL ARCHIVO --------
            if file3.name.endswith('.csv'):
                df_fact_temp = pd.read_csv(file3, header=None)
            else:
                df_fact_temp = pd.read_excel(file3, header=None)

            # Busca la fila que contiene 'NRO_LEGALIACION' para identificar los encabezados
            header_row = None
            for i, row in df_fact_temp.iterrows():
                if row.astype(str).str.strip().str.upper().str.startswith("NRO_LEGALIACION").any():
                    header_row = i
                    break

            if header_row is None:
                st.error("❌ No se encontró la fila de columnas que contiene 'NRO_LEGALIACION'")
            else:
                # Relee el archivo usando la fila identificada como encabezado
                if file3.name.endswith('.csv'):
                    df_fact = pd.read_csv(file3, header=header_row)
                else:
                    df_fact = pd.read_excel(file3, header=header_row)

                # Limpia los nombres de las columnas
                df_fact.columns = (
                    df_fact.columns
                    .astype(str)
                    .str.strip()
                    .str.replace('\n', ' ')
                )
                st.success(f"✅ Archivo cargado: {len(df_fact):,} filas")
                st.info(f"📋 Encabezados detectados en fila: {header_row + 1}")

                # Guardar temporalmente en session_state
                st.session_state.temp_df_fact = df_fact

        except Exception as e:
            st.error(f"❌ Error al leer archivo: {e}")

# --- Columna 4: Facturación Electrónica ---
with col4:
    st.subheader("Facturación electrónica")

    file4 = st.file_uploader("Sube el archivo de Facturación electrónica", type=["xlsx", "xls", "csv"], key="file4")

    if file4 is not None:
        try:
            # -------- LECTURA ROBUSTA DEL ARCHIVO --------
            if file4.name.endswith('.csv'):
                df_fact_elec_temp = pd.read_csv(file4, header=None)
            else:
                df_fact_elec_temp = pd.read_excel(file4, header=None)

            # Busca la fila que contiene 'IDENTIFICACION' para identificar los encabezados
            header_row = None
            for i, row in df_fact_elec_temp.iterrows():
                if row.astype(str).str.strip().str.upper().str.startswith("IDENTIFICACION").any():
                    header_row = i
                    break

            if header_row is None:
                st.error("❌ No se encontró la fila de columnas que contiene 'IDENTIFICACION'")
            else:
                # Relee el archivo usando la fila identificada como encabezado
                if file4.name.endswith('.csv'):
                    df_fact_elec = pd.read_csv(file4, header=header_row)
                else:
                    df_fact_elec = pd.read_excel(file4, header=header_row)

                # Limpia los nombres de las columnas
                df_fact_elec.columns = (
                    df_fact_elec.columns
                    .astype(str)
                    .str.strip()
                    .str.replace('\n', ' ')
                )
                st.success(f"✅ Archivo cargado: {len(df_fact_elec):,} filas")
                st.info(f"📋 Encabezados detectados en fila: {header_row + 1}")

                # Guardar temporalmente en session_state
                st.session_state.temp_df_fact_elec = df_fact_elec

        except Exception as e:
            st.error(f"❌ Error al leer archivo: {e}")

st.markdown("---")

# --- SECCIÓN DE GUARDADO PARA FACTURACIÓN ---
# Solo se muestra cuando ambos archivos están cargados
if 'temp_df_fact' in st.session_state and 'temp_df_fact_elec' in st.session_state:
    st.success("✅ Ambos archivos de facturación están listos para guardar")

    col_resumen1, col_resumen2, col_resumen3 = st.columns([1, 1, 1])

    with col_resumen1:
        st.metric("Facturación", f"{len(st.session_state.temp_df_fact):,} filas")

    with col_resumen2:
        st.metric("Facturación Electrónica", f"{len(st.session_state.temp_df_fact_elec):,} filas")

    with col_resumen3:
        if st.button("💾 Guardar Ambos Archivos de Facturación", use_container_width="stretch", type="primary"):
            try:
                # Guardar Facturación
                st.session_state.df_facturacion = st.session_state.temp_df_fact
                save_local(st.session_state.temp_df_fact, FILES["Facturacion"])

                # Guardar Facturación Electrónica
                st.session_state.df_fact_elec = st.session_state.temp_df_fact_elec
                save_local(st.session_state.temp_df_fact_elec, os.path.join(PERSISTED_DATA_DIR, "df_fact_elec.parquet"))

                # Limpiar temporales
                del st.session_state.temp_df_fact
                del st.session_state.temp_df_fact_elec

                st.success("""✅ Archivos guardados exitosamente:
- Facturación
- Facturación Electrónica
                """)
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error al guardar: {e}")

elif 'temp_df_fact' in st.session_state or 'temp_df_fact_elec' in st.session_state:
    st.info("ℹ️ Sube ambos archivos de facturación para poder guardarlos")

    if 'temp_df_fact' in st.session_state:
        st.write("✅ Facturación cargado")
    else:
        st.write("⏳ Falta Facturación")

    if 'temp_df_fact_elec' in st.session_state:
        st.write("✅ Facturación Electrónica cargado")
    else:
        st.write("⏳ Falta Facturación Electrónica")

st.markdown("---")

# --- BARRA LATERAL (FILTROS GLOBALES) ---
st.sidebar.header("📊 Estado de Datos")

# Muestra el estado de carga de cada dataset en la barra lateral
for nombre, key in [("PPL", "df_ppl"), ("Convenios", "df_convenios"),
                    ("RIPS", "df_rips"), ("Facturación", "df_facturacion")]:
    df = st.session_state.get(key)
    if df is not None and not df.empty:
        st.sidebar.success(f"✅ {nombre}: {len(df):,} registros")
    else:
        st.sidebar.warning(f"⚠️ {nombre}: Sin datos")

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Filtros de Análisis")

# --- Filtro de Tipo de Legalización ---
# Permite seleccionar entre PPL y Convenios
tipo_legalizacion = st.sidebar.multiselect(
    "Tipo de Legalización",
    ["PPL", "Convenios"],
    default=["PPL", "Convenios"]
)

# --- Filtro de Usuario/Facturador ---
# Recolecta todos los usuarios únicos de todos los datasets cargados
facturadores_total = []
for df_name in ['df_ppl', 'df_convenios', 'df_rips', 'df_facturacion']:
    df_temp = st.session_state.get(df_name)
    if df_temp is not None and not df_temp.empty:
        col_u = 'USUARIO' if 'USUARIO' in df_temp.columns else 'Usuario'
        if col_u in df_temp.columns:
            facturadores_total.extend(df_temp[col_u].dropna().unique())

sel_usuarios = st.sidebar.multiselect(
    "Seleccionar Facturador",
    ['Todos'] + sorted(list(set(facturadores_total))),
    default=['Todos']
)

# --- Filtro de Rango de Fechas ---
# Por defecto muestra los últimos 30 días
start_date, end_date = st.sidebar.date_input(
    "Rango de fechas",
    [datetime.date.today() - datetime.timedelta(days=30), datetime.date.today()]
)

# --- Botón para limpiar todos los datos ---
# Elimina los archivos Parquet y reinicia el session_state
if st.sidebar.button("🗑️ Limpiar todos los datos", use_container_width="stretch"):
    for key in FILES.keys():
        filepath = FILES[key]
        if os.path.exists(filepath):
            os.remove(filepath)
        st.session_state[f"df_{key.lower()}"] = None
    st.sidebar.success("✅ Datos limpiados")
    st.rerun()


# --- FUNCIÓN MAESTRA DE VISUALIZACIÓN ---
def procesar_y_graficar(df, titulo, es_legalizacion=False):
    """
    Procesa y visualiza los datos de productividad según los filtros activos.

    Genera dos tipos de visualizaciones según el estado de los filtros:
    1. Modo General (sin filtro de usuario): Gráfico de barras horizontal con distribución porcentual
    2. Modo Comparativo (con filtro de usuario): Gráfico de líneas temporal + tabla resumen

    Args:
        df (pd.DataFrame): DataFrame con los datos a visualizar.
        titulo (str): Título descriptivo de la sección (ej: "Legalizaciones", "Facturación").
        es_legalizacion (bool): True si los datos corresponden a legalizaciones,
                               lo que activa el filtro por tipo (PPL/Convenios).

    Returns:
        None: Genera visualizaciones directamente en Streamlit.

    Comportamiento:
        - Normaliza automáticamente las columnas de Usuario y Fecha
        - Aplica filtros de tipo, fecha y usuario según configuración
        - Muestra advertencias si no hay datos después de filtrar
        - Genera métricas, gráficos y tablas adaptados al contexto
    """
    if df is None or df.empty:
        st.info(f"No hay datos cargados para la sección de {titulo}")
        return

    # Normalización de columnas de Usuario y Fecha
    # Busca variaciones comunes de los nombres de columnas
    col_u = None
    for posible_col_u in ['USUARIO', 'Usuario', 'usuario', 'USUARIO FACTURÓ']:
        if posible_col_u in df.columns:
            col_u = posible_col_u
            break

    col_f = next((c for c in ['FECHA_REAL', 'FECHA_FACTURA', 'FECHA', 'Fecha', 'fecha', 'FECHA RADICACIÓN'] if c in df.columns), None)

    # Filtro por tipo (solo aplica para legalizaciones)
    if es_legalizacion and 'Tipo_Leg' in df.columns:
        df = df[df['Tipo_Leg'].isin(tipo_legalizacion)]

    # Filtro de Fecha
    # Convierte la columna de fecha a datetime y filtra por el rango seleccionado
    if col_f:
        df[col_f] = pd.to_datetime(df[col_f], errors='coerce')
        df = df.dropna(subset=[col_f])
        df = df[(df[col_f].dt.date >= start_date) & (df[col_f].dt.date <= end_date)]

    # Determina si hay un filtro activo de usuario
    es_filtro_activo = 'Todos' not in sel_usuarios and len(sel_usuarios) > 0
    if es_filtro_activo and col_u is not None:
        df = df[df[col_u].isin(sel_usuarios)]

    # Si no hay columna de usuario pero se solicita filtro de usuario
    if es_filtro_activo and col_u is None:
        st.warning(f"⚠️ No se encontró columna de usuario en {titulo}. No se puede filtrar por usuario.")
        return

    if df.empty:
        st.warning(f"No hay datos para mostrar en {titulo} con los filtros actuales.")
        return

    # Muestra métrica de total de registros
    st.metric(f"Total Registros ({titulo})", f"{len(df):,}")

    if not es_filtro_activo:
        # --- MODO GENERAL: GRÁFICO DE BARRAS + TABLA % ---
        # Muestra la productividad general de todos los usuarios
        st.subheader(f"Productividad General: {titulo}")
        fig, ax = plt.subplots(figsize=(10, 6))
        counts = df[col_u].value_counts().reset_index()
        counts.columns = ['Usuario', 'Conteo']

        # Crea gráfico de barras horizontal con etiquetas de valor
        sns.barplot(data=counts, y='Usuario', x='Conteo', palette='viridis', ax=ax)
        for i, v in enumerate(counts['Conteo']):
            ax.text(v + 0.1, i, str(int(v)), color='black', va='center', fontweight='bold')

        ax.set_xlabel("Cantidad Total")
        st.pyplot(fig)

        # Muestra tabla con distribución porcentual
        st.subheader(f"Distribución Porcentual - {titulo}")
        counts['%'] = (counts['Conteo'] / counts['Conteo'].sum() * 100).round(2)
        st.table(counts.style.format({'%': '{:.2f}%'}))

    else:
        # --- MODO COMPARATIVO: LINEPLOT + TABLA RESUMEN ---
        # Compara la evolución temporal de los usuarios seleccionados
        st.subheader(f"Comparativa de Evolución Temporal ({titulo})")
        if col_f:
            df['Dia_Evolucion'] = df[col_f].dt.date
            evol = df.groupby(['Dia_Evolucion', col_u]).size().reset_index(name='Cuenta')

            # Crea gráfico de líneas mostrando evolución día a día
            fig2, ax2 = plt.subplots(figsize=(12, 5))
            sns.lineplot(data=evol, x='Dia_Evolucion', y='Cuenta', hue=col_u, marker='o', ax=ax2)
            ax2.grid(True, linestyle='--', alpha=0.6)
            plt.xticks(rotation=45)
            ax2.set_ylabel("Productividad Diaria")
            st.pyplot(fig2)

        # Muestra tabla resumen de usuarios seleccionados
        st.subheader(f"Resumen de Usuarios Seleccionados")
        resumen_sel = df[col_u].value_counts().reset_index()
        resumen_sel.columns = ['Usuario', 'Total Realizado']
        st.table(resumen_sel)


# --- TABS (PÁGINAS) ---
# Organiza el dashboard en tres pestañas principales
tab_leg, tab_rips, tab_fact = st.tabs(["📁 Legalizaciones", "📄 RIPS", "💰 Facturación"])

# --- Pestaña de Legalizaciones ---
# Combina datos de PPL y Convenios para análisis conjunto
with tab_leg:
    list_leg = []
    if st.session_state.df_ppl is not None and not st.session_state.df_ppl.empty:
        d_p = st.session_state.df_ppl.copy()
        d_p['Tipo_Leg'] = 'PPL'
        list_leg.append(d_p)
    if st.session_state.df_convenios is not None and not st.session_state.df_convenios.empty:
        d_c = st.session_state.df_convenios.copy()
        d_c['Tipo_Leg'] = 'Convenios'
        list_leg.append(d_c)

    if list_leg:
        df_leg_total = pd.concat(list_leg, ignore_index=True)

        procesar_y_graficar(df_leg_total, "Legalizaciones", es_legalizacion=True)

    else:
        st.info("Carga el archivo de legalizaciones para visualizar los datos.")

# --- Pestaña de RIPS ---
with tab_rips:
    procesar_y_graficar(st.session_state.df_rips, "RIPS")

# --- Pestaña de Facturación ---
# Incluye la integración con facturación electrónica y opción de descarga
with tab_fact:
    # Enriquece los datos de facturación con información de usuario desde facturación electrónica
    df_fact_final = buscar_usuario_en_fact_electronica(
        st.session_state.get('df_facturacion'),
        st.session_state.get('df_fact_elec')
    )

    st.subheader("📥 Descarga de Facturación con Usuario")

    if df_fact_final is None or df_fact_final.empty:
        st.warning("⚠️ No hay datos de facturación para mostrar")
    else:
        st.write("Total filas:", len(df_fact_final))

        # Genera archivo Excel en memoria para descarga
        buffer = BytesIO()
        df_fact_final.to_excel(buffer, index=False)
        buffer.seek(0)

        st.download_button(
            "⬇️ Descargar Excel – Facturación con Usuario",
            buffer,
            "facturacion_con_usuario.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    procesar_y_graficar(df_fact_final, "Facturación")