"""Billing validators."""

import pandas as pd

from .common_validator import MSG_VALIDATION_SUCCESS, is_empty_dataframe

MSG_MISSING_BILLING_ID = "Missing NRO_LEGALIACION or NRO_LEGALIZACION column"
BILLING_ID_COLUMN_CANDIDATES = ("NRO_LEGALIACION", "NRO_LEGALIZACION")


def validate_billing_dataframe(df: pd.DataFrame):
    """Validate billing dataframe schema."""
    if is_empty_dataframe(df):
        return False, MSG_MISSING_BILLING_ID

    has_billing_id = any(col in df.columns for col in BILLING_ID_COLUMN_CANDIDATES)
    if not has_billing_id:
        return False, MSG_MISSING_BILLING_ID

    return True, MSG_VALIDATION_SUCCESS
