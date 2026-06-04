"""Common DataFrame validators."""

import pandas as pd

MSG_VALIDATION_SUCCESS = "Validation successful"
MSG_MISSING_USER_OR_DATE = "Missing USER or DATE columns"
MSG_MISSING_COLUMNS = "Missing columns: {columns}"


def is_empty_dataframe(df: pd.DataFrame | None) -> bool:
    """Return True when dataframe is None or empty."""
    return df is None or df.empty


def coerce_variants(column_variants):
    """Normalize column variants input into a list."""
    if column_variants is None:
        return []
    if isinstance(column_variants, str):
        return [column_variants]
    return list(column_variants)


def validate_columns_presence(df: pd.DataFrame, required_columns):
    """Validate that dataframe contains all required columns."""
    required = list(required_columns or [])
    if is_empty_dataframe(df):
        return False, required

    missing = [col for col in required if col not in df.columns]
    return len(missing) == 0, missing


def find_first_column_variant(df: pd.DataFrame, column_variants):
    """Find first matching column name from provided variants."""
    if is_empty_dataframe(df):
        return None

    for variant in coerce_variants(column_variants):
        if variant in df.columns:
            return variant

    return None

