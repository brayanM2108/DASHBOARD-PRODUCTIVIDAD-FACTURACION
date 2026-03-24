"""
Data loading and persistence
============================
Functions to load files from different sources and persist processed data as Parquet.
"""

import io
from typing import Any, Mapping

import pandas as pd
import streamlit as st

from config.settings import FACTURADORES_FILE, FACTURADORES_SHEET, FILES
from utils.file_helpers import load_from_parquet, read_file_robust, save_to_parquet

# Canonical dataset keys (English)
DATASET_TO_FILE_KEY = {
    "ppl_legalizations": "PPL",
    "agreement_legalizations": "Convenios",
    "rips": "RIPS",
    "billing": "Facturacion",
    "billers": "Facturadores",
    "electronic_billing": "FacturacionElectronica",
    "administrative_processes": "ArchivoProcesos",
}

# Required columns for processes dataset
REQUIRED_PROCESS_COLUMNS = ("FECHA", "NOMBRE", "DOCUMENTO", "PROCESO", "CANTIDAD")

# Error messages
ERROR_MISSING_PROCESS_COLUMNS = "Missing required process columns: {columns}"
ERROR_PROCESS_LOAD_FAILED = "Failed to load processes dataset: {error}"



def _normalize_columns_upper(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize dataframe columns to stripped uppercase."""
    df.columns = df.columns.astype(str).str.strip().str.upper()
    return df


def _build_google_sheets_export_url(file_or_url: Any) -> Any:
    """
    Convert a Google Sheets edit URL into an Excel export URL.
    If input is not a Google Sheets URL, return it unchanged.
    """
    if not isinstance(file_or_url, str):
        return file_or_url

    if "docs.google.com/spreadsheets" not in file_or_url:
        return file_or_url

    if "/edit" in file_or_url and "/d/" in file_or_url:
        sheet_id = file_or_url.split("/d/")[1].split("/")[0]
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"

    return file_or_url


def load_all_persisted_frames() -> dict[str, pd.DataFrame | None]:
    """Load all persisted parquet datasets from parquet."""
    """Load all persisted parquet datasets using canonical English keys."""
    datasets = {}
    for dataset_key, file_key in DATASET_TO_FILE_KEY.items():
        datasets[dataset_key] = load_from_parquet(FILES[file_key])
    return datasets

def save_all_persisted_frames(data_by_dataset: Mapping[str, pd.DataFrame]) -> dict[str, bool]:
    """Persist all provided datasets as parquet using canonical English keys."""
    results: dict[str, bool] = {}

    for dataset_key, df in data_by_dataset.items():
        file_key = DATASET_TO_FILE_KEY.get(dataset_key)
        if file_key is None:
            continue
        results[dataset_key] = save_to_parquet(df, FILES[file_key])

    return results


def _load_billers_from_secrets(secrets_source: Mapping[str, Any] | None = None) -> pd.DataFrame | None:
    """
    Load billers master dataset from Streamlit secrets.
    Supports both legacy and English secret keys:
    - facturadores.data
    - billers.data
    """
    secrets = secrets_source
    if secrets is None:
        try:
            secrets = st.secrets
        except Exception:
            secrets = {}

    try:
        if "billers" in secrets and "data" in secrets["billers"]:
            csv_data = secrets["billers"]["data"]
            df = pd.read_csv(io.StringIO(csv_data))
            return _normalize_columns_upper(df)

        if "facturadores" in secrets and "data" in secrets["facturadores"]:
            csv_data = secrets["facturadores"]["data"]
            df = pd.read_csv(io.StringIO(csv_data))
            return _normalize_columns_upper(df)

    except Exception:
        return None

    return None


def _load_billers_from_file() -> pd.DataFrame | None:
    """Load billers master dataset from local Excel file."""
    try:
        df = pd.read_excel(FACTURADORES_FILE, sheet_name=FACTURADORES_SHEET)
        return _normalize_columns_upper(df)
    except Exception:
        return None


def load_billers_master(secrets_source: Mapping[str, Any] | None = None) -> pd.DataFrame | None:
    """
    Load billers master data.
    Priority:
    1) Streamlit secrets (production)
    2) Local Excel file (development)
    """
    df = _load_billers_from_secrets(secrets_source=secrets_source)
    if df is not None:
        return df

    return _load_billers_from_file()


def load_uploaded_dataframe(file, header_marker: str) -> pd.DataFrame | None:
    """Load uploaded file by auto-detecting real header row using marker."""
    df, _ = read_file_robust(file, header_marker)
    return df


def load_processes_data(file_or_url) -> pd.DataFrame:
    """
    Load administrative processes data from uploaded Excel file or Google Sheets URL.
    """
    try:
        source = _build_google_sheets_export_url(file_or_url)
        df = pd.read_excel(source)
        df = _normalize_columns_upper(df)

        missing = [col for col in REQUIRED_PROCESS_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(ERROR_MISSING_PROCESS_COLUMNS.format(columns=", ".join(missing)))

        df["FECHA"] = pd.to_datetime(df["FECHA"], format="%d/%m/%Y", errors="coerce")
        df["CANTIDAD"] = pd.to_numeric(df["CANTIDAD"], errors="coerce")

        df = df.dropna(subset=["FECHA", "NOMBRE", "CANTIDAD"])
        return df

    except Exception as exc:
        raise ValueError(ERROR_PROCESS_LOAD_FAILED.format(error=str(exc))) from exc

def extract_google_sheet_ids(sheet_url: str) -> tuple[str | None, str]:
    """
    Extract sheet_id and gid from a Google Sheets URL.
    Returns (None, "0") when sheet_id cannot be extracted.
    """
    import re

    if not isinstance(sheet_url, str) or not sheet_url.strip():
        return None, "0"

    id_match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", sheet_url)
    if not id_match:
        return None, "0"

    sheet_id = id_match.group(1)

    gid = "0"
    gid_match = re.search(r"[#&]gid=([0-9]+)", sheet_url)
    if gid_match:
        gid = gid_match.group(1)

    return sheet_id, gid


def build_google_sheet_csv_url(sheet_id: str, gid: str = "0") -> str:
    """
    Build CSV export URL from sheet_id and gid.
    """
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


def load_google_sheet_csv(sheet_url: str) -> pd.DataFrame:
    """
    Load raw dataframe from Google Sheets using CSV export endpoint.
    """
    sheet_id, gid = extract_google_sheet_ids(sheet_url)
    if not sheet_id:
        raise ValueError("Could not extract Google Sheet ID from URL.")

    csv_url = build_google_sheet_csv_url(sheet_id, gid)
    return pd.read_csv(csv_url)


def persist_administrative_processes(df: pd.DataFrame) -> dict[str, bool]:
    """
    Persist processed administrative processes dataframe using canonical key.
    """
    return save_all_persisted_frames({"administrative_processes": df})

