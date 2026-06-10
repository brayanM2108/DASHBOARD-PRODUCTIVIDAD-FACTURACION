"""
Global Productivity Dashboard Settings
=====================================================
Contains all constants, file paths, and settings shared by the entire application.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def get_env_var(key, default=""):
    return os.getenv(key, default)


PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_PERSISTED_DATA_DIR = PROJECT_ROOT / "backend" / "persisted_data"
PERSISTED_DATA_DIR = Path(get_env_var("PERSISTED_DATA_DIR", str(DEFAULT_PERSISTED_DATA_DIR)))
PERSISTED_DATA_DIR.mkdir(parents=True, exist_ok=True)

FACTURADORES_FILE = str(PROJECT_ROOT / "backend" / "FACTURADORES.xlsx")
FACTURADORES_SHEET = 0
PROCESOS_SHEET_URL = get_env_var("PROCESOS_SHEET_URL", "")

FILES = {
    "Legalizaciones": str(PERSISTED_DATA_DIR / "legalizations.parquet"),
    "Facturacion": str(PERSISTED_DATA_DIR / "df_facturacion.parquet"),
    "Facturadores": str(PERSISTED_DATA_DIR / "df_facturadores.parquet"),
    "FacturacionElectronica": str(PERSISTED_DATA_DIR / "df_fact_elec.parquet"),
    "ArchivoProcesos": str(PERSISTED_DATA_DIR / "df_procesos.parquet"),
    "Rips": str(PERSISTED_DATA_DIR / "df_rips.parquet"),
}

VALID_STATES_LEGALIZATIONS = ["ACTIVA"]
VALID_STATES_INVOICING_ELECTRONIC = ["ACTIVO"]

COLUMN_MARKERS = {
    "legalizaciones": "ID_LEGALIZACION",
    "facturacion": "NRO_LEGALIACION",
    "facturacion_electronica": "IDENTIFICACION",
    "procesos": "PROCESO",
    "rips": "ESTADO_COMPLETITUD",
}

COLUMN_NAMES = {
    "usuario": ["USUARIO", "USUARIO FACTURÃ“", "USUARIO FACTURO", "USUARIO FACTUR", "USUARIO_FACTURO"],
    "fecha": ["FECHA_REAL", "FECHA_FACTURA", "FECHA", "FECHA RADICACIÃ“N", "FECHA LEGALIZACIÃ“N", "FECHA LEGALIZACION"],
    "estado": ["ESTADO"],
    "convenio": "CONVENIO",
}

COLUMN_NAMES_BILLING = {
    "usuario": ["USUARIO"],
    "fecha": ["FECHA FACTURA"],
    "estado": ["Estado"],
    "convenio": "CONVENIO",
}

COLUMN_NAMES_LEGALIZATIONS = {
    "usuario": ["USUARIO"],
    "fecha": ["FECHA_REAL"],
    "estado": "ESTADO",
    "convenio": "CONVENIO",
}

COLUMN_NAMES_RIPS = {
    "usuario": ["USUARIO_QUE_COMPLETA_RIPS"],
    "fecha": ["FECHA_COMPLETADO_RIPS"],
    "estado": "ESTADO_COMPLETITUD",
}

VALID_STATES_RIPS = ["COMPLETO"]

PPL_NAME = "Patrimonio Autonomo Fondo Atención Salud PPL 2024"

NAMES_AGREEMENTS = {
    "PPL": PPL_NAME,
    "CEX": [
        "CEX - E.P.S. CAPITAL SALUD SUBSIDIADO 2025",
        "CEX - E.P.S. NUEVA EPS CONTRIBUTIVO 2025",
        "CEX - E.P.S. CAPITAL SALUD CONTRIBUTIVO 2025",
        "CEX - E.P.S. NUEVA EPS SUBSIDIADO 2025",
        "CEX - E.P.S. SALUD TOTAL CONTRIBUTIVO 2025",
        "CEX - E.P.S. SALUD TOTAL SUBSIDIADO 2025",
        "CEX - POSITIVA COMPAÃ‘IA DE SEGUROS S.A.",
    ],
    "PHD": [
        "PHD - E.P.S. NUEVA EPS CONTRIBUTIVO",
        "PHD - E.P.S. CAPITAL SALUD SUBSIDIADO",
        "PHD - E.P.S. SALUD TOTAL SUBSIDIADO",
        "PHD - E.P.S. SALUD TOTAL CONTRIBUTIVO",
        "PHD-E.P.S. SURA CONTRIBUTIVO",
        "PHD - E.P.S. NUEVA EPS SUBSIDIADO",
        "PHD - E.P.S. CAPITAL SALUD CONTRIBUTIVO",
        "ALTA TEMPRANA PHD - E.P.S. NUEVA EPS SUBSIDIADO",
        "PHD - E.P.S. SURA SUBSIDIADO",
        "ALTA TEMPRANA PHD - E.P.S. NUEVA EPS CONTRIBUTIVO",
        "521 PHD - E.P.S. SURA CONTRIBUTIVO",
    ],
    "PIR": [
        "PIR - E.P.S. SALUD TOTAL CONTRIBUTIVO",
        "PIR - E.P.S. SALUD TOTAL SUBSIDIADO",
        "PIR - E.P.S. NUEVA EPS SUBSIDIADO",
        "PIR - E.P.S. NUEVA EPS CONTRIBUTIVO",
        "PIR - E.P.S. CAPITAL SALUD SUBSIDIADO 2024",
        "PIR - E.P.S. SURA CONTRIBUTIVO",
        "PIR - E.P.S. SURA SUBSIDIADO",
        "PIR - E.P.S. CAPITAL SALUD CONTRIBUTIVO 2024",
    ],
    "FOMAG": "FONDO NACIONAL DE PRESTACIONES SOCIALES DEL",
    "IDIPROM": [
        "IDIPROM SDIS - E.P.S. CAPITAL SALUD SUBSIDIADO 2024",
        "IDIPROM SDIS- E.P.S. CAPITAL SALUD CONTRIBUTIVO 2024",
    ],
    "PGP SOACHA": "PGP SOACHA - E.P.S. NUEVA EPS CONTRIBUTIVO",
}

PAGE_CONFIG = {
    "page_title": "Dashboard de Productividad",
    "page_icon": "ðŸ“Š",
    "layout": "wide",
}

PLOT_CONFIG = {
    "figsize_barplot": (10, 6),
    "figsize_lineplot": (12, 5),
    "palette": "viridis",
}
