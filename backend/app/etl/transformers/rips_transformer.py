"""RIPS DataFrame transformers."""

import pandas as pd

from ..utils.dataframe_helpers import normalize_text_series
from ..utils.date_helpers import parse_date_column
from ..validators.common_validator import find_first_column_variant
from ...utils.config.settings import COLUMN_NAMES_RIPS, VALID_STATES_RIPS


def prepare_rips_dataframe(df: pd.DataFrame) -> pd.DataFrame | None:
    if df is None or df.empty:
        return None

    result_df = df.copy()

    state_col = find_first_column_variant(result_df, COLUMN_NAMES_RIPS["estado"])
    if state_col and state_col in result_df.columns:
        result_df[state_col] = normalize_text_series(result_df[state_col])
        allowed = {s.strip().upper() for s in VALID_STATES_RIPS}
        result_df = result_df[result_df[state_col].isin(allowed)].copy()

    date_col = find_first_column_variant(result_df, COLUMN_NAMES_RIPS["fecha"])
    if date_col:
        result_df = parse_date_column(result_df, date_col)
        result_df = result_df.dropna(subset=[date_col])

    return result_df.reset_index(drop=True)
