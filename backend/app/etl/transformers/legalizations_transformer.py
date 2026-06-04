"""Legalizations DataFrame transformers."""

import pandas as pd

from ..utils.dataframe_helpers import normalize_text_series
from ..utils.date_helpers import parse_date_column
from ...utils.config.settings import PPL_NAME, VALID_STATES_LEGALIZATIONS


def split_legalizations(
    df: pd.DataFrame,
    state_column: str = "ESTADO",
    date_column: str = "FECHA LEGALIZACION",
    agreement_column: str = "CONVENIO",
) -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
    """Process legalizations dataframe and split into PPL and agreements."""
    if df is None or df.empty:
        return None, None

    result_df = df.copy()
    result_df = parse_date_column(result_df, date_column)

    if state_column in result_df.columns:
        result_df[state_column] = normalize_text_series(result_df[state_column])
        result_df = result_df[result_df[state_column].isin(VALID_STATES_LEGALIZATIONS)]

    if agreement_column not in result_df.columns:
        return None, None

    ppl_df = result_df[result_df[agreement_column] == PPL_NAME].copy()
    agreements_df = result_df[result_df[agreement_column] != PPL_NAME].copy()
    return ppl_df, agreements_df

