"""Billers master data loader."""

import io
from collections.abc import Mapping
from typing import Any

import pandas as pd

from ..utils.dataframe_helpers import normalize_columns_upper_in_place
from ...utils.config.settings import FACTURADORES_FILE, FACTURADORES_SHEET


def normalize_billers_document_column(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize DOCUMENTO values to plain digit strings for reliable matching."""
    if "DOCUMENTO" not in df.columns:
        return df

    doc_series = df["DOCUMENTO"].astype(str).str.strip()
    doc_series = doc_series.str.replace(r"\.0$", "", regex=True)
    df["DOCUMENTO"] = doc_series
    return df


def load_billers_from_secrets(secrets_source: Mapping[str, Any] | None = None) -> pd.DataFrame | None:
    """Load billers master dataset from an injected secrets mapping."""
    secrets = secrets_source or {}

    try:
        if "billers" in secrets and "data" in secrets["billers"]:
            csv_data = secrets["billers"]["data"]
            df = pd.read_csv(io.StringIO(csv_data))
            df = normalize_columns_upper_in_place(df)
            return normalize_billers_document_column(df)

        if "facturadores" in secrets and "data" in secrets["facturadores"]:
            csv_data = secrets["facturadores"]["data"]
            df = pd.read_csv(io.StringIO(csv_data))
            df = normalize_columns_upper_in_place(df)
            return normalize_billers_document_column(df)

    except Exception:
        return None

    return None


def load_billers_from_file() -> pd.DataFrame | None:
    """Load billers master dataset from local Excel file."""
    try:
        df = pd.read_excel(FACTURADORES_FILE, sheet_name=FACTURADORES_SHEET)
        df = normalize_columns_upper_in_place(df)
        return normalize_billers_document_column(df)
    except Exception:
        return None


def load_billers_master(secrets_source: Mapping[str, Any] | None = None) -> pd.DataFrame | None:
    """Load billers master data from injected secrets first, then local Excel."""
    df = load_billers_from_secrets(secrets_source=secrets_source)
    if df is not None:
        return df

    return load_billers_from_file()


def load_billers_master_cached(secrets_source: Mapping[str, Any] | None = None) -> pd.DataFrame | None:
    """Compatibility wrapper without framework-level caching."""
    return load_billers_master(secrets_source=secrets_source)
