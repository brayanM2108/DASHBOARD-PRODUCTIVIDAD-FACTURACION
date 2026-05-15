"""
Global Productivity Dashboard Settings
=====================================================
Contains all constants, file paths, and settings shared by the entire application.
"""


import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables (local)
load_dotenv()

# Helper function to obtain environment variables or secrets
def get_env_var(key, default=''):
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except:
        return os.getenv(key, default)

PERSISTED_DATA_DIR = "persisted_data"
os.makedirs(PERSISTED_DATA_DIR, exist_ok=True)

# --- Master Files ---
FACTURADORES_FILE = "FACTURADORES.xlsx"
FACTURADORES_SHEET = 0

# --- URL de Google Sheets ---
PROCESOS_SHEET_URL = st.secrets.get('PROCESOS_SHEET_URL', '')

# --- Google Sheets URL ---
FILES = {
    "PPL": os.path.join(PERSISTED_DATA_DIR, "df_ppl.parquet"),
    "Convenios": os.path.join(PERSISTED_DATA_DIR, "df_convenios.parquet"),
    "RIPS": os.path.join(PERSISTED_DATA_DIR, "df_rips.parquet"),
    "Facturacion": os.path.join(PERSISTED_DATA_DIR, "df_facturacion.parquet"),
    "Facturadores": os.path.join(PERSISTED_DATA_DIR, "df_facturadores.parquet"),
    "FacturacionElectronica": os.path.join(PERSISTED_DATA_DIR, "df_fact_elec.parquet"),
    "ArchivoProcesos": os.path.join(PERSISTED_DATA_DIR, "df_procesos.parquet")
}

# --- Valid States ---
VALID_STATES_LEGALIZATIONS = ['ACTIVA']
VALID_STATES_RIPS = ['COMPLETO']
VALID_STATES_INVOICING_ELECTRONIC = ['ACTIVO']

# --- Column identifiers ---
# Markers for detecting headers in files
COLUMN_MARKERS = {
    "legalizaciones": "ID_LEGALIZACION",
    "rips": "CÓDIGO",
    "facturacion": "NRO_LEGALIACION",
    "facturacion_electronica": "IDENTIFICACION",
    "procesos": "PROCESO"
}

# --- Normalized Column Names ---
# IMPORTANT: All in uppercase because the columns are normalized to uppercase
COLUMN_NAMES = {
    "usuario": ["USUARIO", "USUARIO FACTURÓ", "USUARIO FACTURO", "USUARIO FACTUR", "USUARIO_FACTURO"],
    "fecha": ["FECHA_REAL", "FECHA_FACTURA", "FECHA", "FECHA RADICACIÓN", "FECHA LEGALIZACIÓN", "FECHA LEGALIZACION"],
    "estado": ["ESTADO"],
    "convenio": "CONVENIO"
}

COLUMN_NAMES_BILLING = {
    "usuario": ["USUARIO"],
    "fecha": ["FECHA FACTURA"],
    "estado": ["Estado"],
    "convenio": "CONVENIO"
}

COLUMN_NAMES_LEGALIZATIONS = {
    "usuario": ["USUARIO", "USUARIO FACTURÓ", "USUARIO FACTURO", "USUARIO FACTUR", "USUARIO_FACTURO"],
    "fecha": ["FECHA_REAL"],
    "estado": "ESTADO",
    "convenio": "CONVENIO",
}

# --- Special Values ---
PPL_NAME = "Patrimonio Autonomo Fondo Atención Salud PPL 2024"

NAMES_AGREEMENTS = {
    "PPL": PPL_NAME,
    "CEX": ["CEX - E.P.S. CAPITAL SALUD SUBSIDIADO 2025", "CEX - E.P.S. NUEVA EPS CONTRIBUTIVO 2025",
    "CEX - E.P.S. CAPITAL SALUD CONTRIBUTIVO 2025", "CEX - E.P.S. NUEVA EPS SUBSIDIADO 2025",
    "CEX - E.P.S. SALUD TOTAL CONTRIBUTIVO 2025", "CEX - E.P.S. SALUD TOTAL SUBSIDIADO 2025",
    "CEX - POSITIVA COMPAÑIA DE SEGUROS S.A."],
    "PHD": ["PHD - E.P.S. NUEVA EPS CONTRIBUTIVO", "PHD - E.P.S. CAPITAL SALUD SUBSIDIADO", "PHD - E.P.S. SALUD TOTAL SUBSIDIADO",
    "PHD - E.P.S. SALUD TOTAL CONTRIBUTIVO", "PHD-E.P.S. SURA CONTRIBUTIVO", "PHD - E.P.S. NUEVA EPS SUBSIDIADO",
    "PHD - E.P.S. CAPITAL SALUD CONTRIBUTIVO", "ALTA TEMPRANA PHD - E.P.S. NUEVA EPS SUBSIDIADO",
    "PHD - E.P.S. SURA SUBSIDIADO", "ALTA TEMPRANA PHD - E.P.S. NUEVA EPS CONTRIBUTIVO" , "521 PHD - E.P.S. SURA CONTRIBUTIVO"],
    "PIR" : ["PIR - E.P.S. SALUD TOTAL CONTRIBUTIVO", "PIR - E.P.S. SALUD TOTAL SUBSIDIADO",
    "PIR - E.P.S. NUEVA EPS SUBSIDIADO", "PIR - E.P.S. NUEVA EPS CONTRIBUTIVO",
    "PIR - E.P.S. CAPITAL SALUD SUBSIDIADO 2024", "PIR - E.P.S. SURA CONTRIBUTIVO",
    "PIR - E.P.S. SURA SUBSIDIADO", "PIR - E.P.S. CAPITAL SALUD CONTRIBUTIVO 2024"],
    "FOMAG": "FONDO NACIONAL DE PRESTACIONES SOCIALES DEL",
    "IDIPROM": ["IDIPROM SDIS - E.P.S. CAPITAL SALUD SUBSIDIADO 2024", "IDIPROM SDIS- E.P.S. CAPITAL SALUD CONTRIBUTIVO 2024"],
    "PGP SOACHA": "PGP SOACHA - E.P.S. NUEVA EPS CONTRIBUTIVO"

}

# --- Streamlit Settings ---
PAGE_CONFIG = {
    "page_title": "Dashboard de Productividad",
    "page_icon": "📊",
    "layout": "wide"
}

# --- Display settings ---
PLOT_CONFIG = {
    "figsize_barplot": (10, 6),
    "figsize_lineplot": (12, 5),
    "palette": "viridis"
}
