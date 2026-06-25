"""Billers master data loader."""

import io
import json
import logging
from collections.abc import Mapping
from typing import Any

import pandas as pd

from ..utils.dataframe_helpers import normalize_columns_upper_in_place
from ...utils.config.settings import FACTURADORES_FILE

logger = logging.getLogger(__name__)


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

    except Exception as e:
        logger.warning("Failed to load billers from secrets: %s", e)
        return None

    return None


def load_billers_from_file() -> pd.DataFrame | None:
    """Load billers master dataset from local JSON file."""
    try:
        with open(FACTURADORES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        df = normalize_columns_upper_in_place(df)
        return normalize_billers_document_column(df)
    except Exception as e:
        logger.warning("Failed to load billers from file: %s", e)
        return None


def save_billers_to_file(df: pd.DataFrame) -> bool:
    """Persist billers dataframe to the JSON file."""
    try:
        data = df.to_dict(orient="records")
        with open(FACTURADORES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error("Failed to save billers to file: %s", e)
        return False


def load_billers_master(secrets_source: Mapping[str, Any] | None = None) -> pd.DataFrame | None:
    """Load billers master data from injected secrets first, then local JSON."""
    df = load_billers_from_secrets(secrets_source=secrets_source)
    if df is not None:
        return df

    return load_billers_from_file()


def load_billers_master_cached(secrets_source: Mapping[str, Any] | None = None) -> pd.DataFrame | None:
    """Compatibility wrapper without framework-level caching."""
    return load_billers_master(secrets_source=secrets_source)
