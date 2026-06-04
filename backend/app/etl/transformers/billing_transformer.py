"""Billing DataFrame transformers."""

import pandas as pd

from ..utils.date_helpers import parse_date_column


def process_billing_data(
    df: pd.DataFrame,
    date_column: str = "FECHA_FACTURA",
) -> pd.DataFrame | None:
    """Process billing dataframe."""
    if df is None or df.empty:
        return None

    result_df = df.copy()
    return parse_date_column(result_df, date_column)
