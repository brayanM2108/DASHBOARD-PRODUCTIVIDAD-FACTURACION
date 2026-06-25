"""
Global Productivity Dashboard Settings
=====================================================
Contains all constants, file paths, and settings shared by the entire application.
"""
import logging
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

FACTURADORES_FILE = str(Path(__file__).resolve().parent / "facturadores.json")
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
    "documento": "USUARIO_QUE_LEGALIZO"
}

COLUMN_NAMES_RIPS = {
    "documento": ["USUARIO_QUE_COMPLETA_RIPS"],
    "fecha": ["FECHA_COMPLETADO_RIPS"],
    "estado": "ESTADO_COMPLETITUD",
}
COLUMN_NAMES_RADICACION = {
    "usuario": ["USUARIO"],
    "fecha": ["FECHA FACTURA"],
    "factura": ["FACTURA"],
    "fecha_radicado": ["FECHA RADICADO"],
    "radicado_panacea": ["RADICADO PANACEA"],
    "radicado_externo": ["RADICADO EXTERNO"],
}

VALID_STATES_RIPS = ["COMPLETO"]

RADICACION_DAYS_THRESHOLD = 2

WORKING_HOURS_PER_DAY = 8.5
WORKING_HOURS_PER_WEEK = 42

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "process_config.json")


def _load_full_config() -> dict:
    try:
        import json as _json
        with open(_CONFIG_PATH, "r", encoding="utf-8") as _f:
            return _json.load(_f)
    except Exception as e:
        logging.getLogger(__name__).warning("Could not load process_config.json: %s", e)
        return {}


def _load_process_seconds() -> dict:
    data = _load_full_config()
    procs = data.get("processes", [])
    if procs:
        return {p["name"].upper(): p["seconds"] for p in procs}
    return {
        "AUDITAR CUENTAS": 180,
        "DESCARGAR AUTORIZACIONES": 120,
        "DESCARGAR SOPORTES": 60,
        "UNIFICAR SOPORTES": 900,
        "VALIDAR RIPS": 1200,
        "RADICAR CUENTAS": 900,
    }


def _load_module_seconds() -> dict:
    data = _load_full_config()
    mt = data.get("module_times", {})
    return {
        "legalizations": mt.get("legalizations", 90),
        "billing": mt.get("billing", 45),
        "rips": mt.get("rips", 45),
    }


PROCESS_SECONDS = _load_process_seconds()
_module_defaults = _load_module_seconds()
SECONDS_PER_RECORD_LEGALIZATIONS = _module_defaults["legalizations"]
SECONDS_PER_RECORD_BILLING = _module_defaults["billing"]
SECONDS_PER_RECORD_RIPS = _module_defaults["rips"]


def reload_config() -> tuple[dict, dict, dict]:
    global PROCESS_SECONDS, SECONDS_PER_RECORD_LEGALIZATIONS, SECONDS_PER_RECORD_BILLING, SECONDS_PER_RECORD_RIPS
    PROCESS_SECONDS = _load_process_seconds()
    mt = _load_module_seconds()
    SECONDS_PER_RECORD_LEGALIZATIONS = mt["legalizations"]
    SECONDS_PER_RECORD_BILLING = mt["billing"]
    SECONDS_PER_RECORD_RIPS = mt["rips"]
    return PROCESS_SECONDS, mt

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
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

PLOT_CONFIG = {
    "figsize_barplot": (10, 6),
    "figsize_lineplot": (12, 5),
    "palette": "viridis",
}
