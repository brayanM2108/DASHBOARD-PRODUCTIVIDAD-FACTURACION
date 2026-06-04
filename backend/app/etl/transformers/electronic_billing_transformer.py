"""Electronic billing DataFrame transformers."""

import pandas as pd

from ..utils.dataframe_helpers import normalize_text_series
from ..utils.date_helpers import parse_date_column
from ...utils.config.settings import VALID_STATES_INVOICING_ELECTRONIC

def process_electronic_billing_data(
    df: pd.DataFrame,
    state_column: str = "ESTADO",
    date_column: str = "FECHA FACTURA",
) -> pd.DataFrame | None:
    """Process electronic billing dataframe."""
    if df is None or df.empty:
        return None

    result_df = df.copy()
    result_df = parse_date_column(result_df, date_column)

    if state_column in result_df.columns:
        result_df[state_column] = normalize_text_series(result_df[state_column])
        result_df = result_df[result_df[state_column].isin(VALID_STATES_INVOICING_ELECTRONIC)]

    return result_df

