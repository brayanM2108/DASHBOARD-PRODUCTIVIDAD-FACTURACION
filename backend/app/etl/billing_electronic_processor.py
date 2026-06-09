"""
ETL - Electronic Billing Processor
===================================
DataFrame transformations for electronic billing.
"""

import pandas as pd

from .validators import find_first_column_variant
from ..utils.config.settings import COLUMN_NAMES_BILLING

VALUE_COLUMN = "VALOR TERCERO"


def _normalize_user_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip()


def _parse_amount_series(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype(str)
        .str.strip()
        .str.replace(r"[^\d,\.\-]", "", regex=True)
        .str.replace(",", "", regex=False)
    )
    return pd.to_numeric(cleaned, errors="coerce").fillna(0.0)


def _find_user_column(df: pd.DataFrame) -> str | None:
    return find_first_column_variant(df, COLUMN_NAMES_BILLING.get("usuario", []))


def _find_agreement_column(df: pd.DataFrame) -> str | None:
    return find_first_column_variant(df, COLUMN_NAMES_BILLING.get("convenio", []))


def _find_date_column(df: pd.DataFrame) -> str | None:
    return find_first_column_variant(df, COLUMN_NAMES_BILLING.get("fecha", []))


def prepare_electronic_billing_df(df: pd.DataFrame | None) -> pd.DataFrame | None:
    """Standard cleanup for electronic billing productivity calculations."""
    if df is None or df.empty:
        return None

    result_df = df.copy()
    result_df.columns = result_df.columns.astype(str).str.strip().str.upper()

    user_col = _find_user_column(result_df)
    if user_col is None or user_col not in result_df.columns:
        return None
    if VALUE_COLUMN not in result_df.columns:
        return None

    result_df[user_col] = _normalize_user_series(result_df[user_col])
    result_df = result_df[result_df[user_col].notna()]
    result_df = result_df[result_df[user_col] != ""]

    result_df[VALUE_COLUMN] = _parse_amount_series(result_df[VALUE_COLUMN])

    date_col = _find_date_column(result_df)
    if date_col:
        result_df[date_col] = pd.to_datetime(result_df[date_col], errors="coerce")

    return result_df
