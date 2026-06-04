"""Legalizations validators."""

import pandas as pd

from .common_validator import (
    MSG_MISSING_COLUMNS,
    MSG_MISSING_USER_OR_DATE,
    MSG_VALIDATION_SUCCESS,
    find_first_column_variant,
    validate_columns_presence,
)
from ...utils.config.settings import COLUMN_NAMES

LEGALIZATIONS_REQUIRED_COLUMNS = ("ESTADO", "CONVENIO")


def validate_legalizations_dataframe(df: pd.DataFrame):
    """Validate legalizations dataframe schema."""
    user_col = find_first_column_variant(df, COLUMN_NAMES["usuario"])
    date_col = find_first_column_variant(df, COLUMN_NAMES["fecha"])
    if user_col is None or date_col is None:
        return False, MSG_MISSING_USER_OR_DATE

    is_valid, missing = validate_columns_presence(df, LEGALIZATIONS_REQUIRED_COLUMNS)
    if not is_valid:
        return False, MSG_MISSING_COLUMNS.format(columns=", ".join(missing))

    return True, MSG_VALIDATION_SUCCESS
