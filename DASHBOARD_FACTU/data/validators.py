"""
Data validation
===============
Functions to validate dataframe structure and required columns.
"""

import pandas as pd
from config.settings import COLUMN_NAMES

# ---------------------------------------------------------------------------
# Centralized messages
# ---------------------------------------------------------------------------

MSG_VALIDATION_SUCCESS = "Validation successful"
MSG_MISSING_USER_OR_DATE = "Missing USER or DATE columns"
MSG_MISSING_COLUMNS = "Missing columns: {columns}"
MSG_MISSING_BILLING_ID = "Missing NRO_LEGALIACION or NRO_LEGALIZACION column"


# ---------------------------------------------------------------------------
# Validation requirements
# ---------------------------------------------------------------------------

LEGALIZATIONS_REQUIRED_COLUMNS = ("ESTADO", "CONVENIO")
RIPS_REQUIRED_COLUMNS = ("ESTADO",)
E_BILLING_REQUIRED_COLUMNS = ("ESTADO",)
BILLING_ID_COLUMN_CANDIDATES = ("NRO_LEGALIACION", "NRO_LEGALIZACION")


# ---------------------------------------------------------------------------
# Internal helpers
# -----

def _is_empty_dataframe(df: pd.DataFrame | None) -> bool:
    """Return True when dataframe is None or empty."""
    return df is None or df.empty


def _coerce_variants(column_variants):
    """Normalize column variants input into a list."""
    if column_variants is None:
        return []
    if isinstance(column_variants, str):
        return [column_variants]
    return list(column_variants)


def _validate_user_and_date_columns(df: pd.DataFrame):
    """Validate that USER and DATE logical columns exist in dataframe."""
    user_col = find_first_column_variant(df, COLUMN_NAMES["usuario"])
    date_col = find_first_column_variant(df, COLUMN_NAMES["fecha"])

    if user_col is None or date_col is None:
        return False, MSG_MISSING_USER_OR_DATE

    return True, MSG_VALIDATION_SUCCESS


def validate_columns_presence(df: pd.DataFrame, required_columns):
    """
    Validate that dataframe contains all required columns.

    Returns:
        tuple[bool, list]: (is_valid, missing_columns)
    """
    required = list(required_columns or [])
    if _is_empty_dataframe(df):
        return False, required

    missing = [col for col in required if col not in df.columns]
    return len(missing) == 0, missing


def find_first_column_variant(df: pd.DataFrame, column_variants):
    """
    Find first matching column name from provided variants.

    Returns:
        str | None: Matching column name or None.
    """
    if _is_empty_dataframe(df):
        return None

    for variant in _coerce_variants(column_variants):
        if variant in df.columns:
            return variant

    return None


def validate_legalizations_dataframe(df: pd.DataFrame):
    """
    Validate legalizations dataframe schema.

    Returns:
        tuple[bool, str]: (is_valid, message)
    """
    user_date_valid, message = _validate_user_and_date_columns(df)
    if not user_date_valid:
        return False, message

    is_valid, missing = validate_columns_presence(df, LEGALIZATIONS_REQUIRED_COLUMNS)
    if not is_valid:
        return False, MSG_MISSING_COLUMNS.format(columns=", ".join(missing))

    return True, MSG_VALIDATION_SUCCESS


def validate_rips_dataframe(df: pd.DataFrame):
    """
    Validate RIPS dataframe schema.

    Returns:
        tuple[bool, str]: (is_valid, message)
    """
    user_date_valid, message = _validate_user_and_date_columns(df)
    if not user_date_valid:
        return False, message

    is_valid, missing = validate_columns_presence(df, RIPS_REQUIRED_COLUMNS)
    if not is_valid:
        return False, MSG_MISSING_COLUMNS.format(columns=", ".join(missing))

    return True, MSG_VALIDATION_SUCCESS


def validate_billing_dataframe(df: pd.DataFrame):
    """
    Validate billing dataframe schema.

    Returns:
        tuple[bool, str]: (is_valid, message)
    """
    if _is_empty_dataframe(df):
        return False, MSG_MISSING_BILLING_ID

    has_billing_id = any(col in df.columns for col in BILLING_ID_COLUMN_CANDIDATES)
    if not has_billing_id:
        return False, MSG_MISSING_BILLING_ID

    return True, MSG_VALIDATION_SUCCESS


def validate_electronic_billing_dataframe(df: pd.DataFrame):
    """
    Validate electronic billing dataframe schema.

    Returns:
        tuple[bool, str]: (is_valid, message)
    """
    user_date_valid, message = _validate_user_and_date_columns(df)
    if not user_date_valid:
        return False, message

    is_valid, missing = validate_columns_presence(df, E_BILLING_REQUIRED_COLUMNS)
    if not is_valid:
        return False, MSG_MISSING_COLUMNS.format(columns=", ".join(missing))

    return True, MSG_VALIDATION_SUCCESS
