"""Legalizations DataFrame transformers."""

import unicodedata

import pandas as pd

from ..utils.dataframe_helpers import normalize_text_series
from ..utils.date_helpers import parse_date_column
from ..validators.common_validator import find_first_column_variant
from ...utils.config.settings import COLUMN_NAMES, PPL_NAME, VALID_STATES_LEGALIZATIONS

LEGALIZATION_TYPE_COLUMN = "LEGALIZATION_TYPE"
PPL_TYPE = "PPL"
AGREEMENT_TYPE = "AGREEMENT"


def _normalize_key(value: str) -> str:
    """Normalize text for stable comparisons, ignoring accents and casing."""
    normalized = unicodedata.normalize("NFKD", str(value))
    without_accents = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    return without_accents.strip().upper()


def _is_active_state(series: pd.Series) -> pd.Series:
    """Return a boolean mask for active legalizations, tolerating text variants."""
    normalized = normalize_text_series(series).fillna("")
    allowed_states = {state.strip().upper() for state in VALID_STATES_LEGALIZATIONS}
    return (
        normalized.isin(allowed_states)
        | normalized.str.contains("ACTIVA", na=False)
    )


def prepare_legalizations_dataframe(
    df: pd.DataFrame,
    state_column: str = "ESTADO",
    date_column: str = "FECHA REAL",
    agreement_column: str = "CONVENIO",
) -> pd.DataFrame | None:
    """Normalize legalizations and add the mandatory type column."""
    if df is None or df.empty:
        return None

    result_df = df.copy()

    date_variants = list(COLUMN_NAMES["fecha"]) + ["FECHA REAL"]
    detected_date_column = find_first_column_variant(result_df, date_variants) or date_column
    result_df = parse_date_column(result_df, detected_date_column)

    if state_column in result_df.columns:
        result_df[state_column] = normalize_text_series(result_df[state_column])
        result_df = result_df[_is_active_state(result_df[state_column])].copy()

    if agreement_column not in result_df.columns:
        return None

    convenio_normalized = normalize_text_series(result_df[agreement_column])
    ppl_name_normalized = _normalize_key(PPL_NAME)

    result_df[agreement_column] = convenio_normalized
    result_df[LEGALIZATION_TYPE_COLUMN] = AGREEMENT_TYPE
    result_df.loc[
        convenio_normalized.map(_normalize_key) == ppl_name_normalized,
        LEGALIZATION_TYPE_COLUMN,
    ] = PPL_TYPE

    return result_df.reset_index(drop=True)
