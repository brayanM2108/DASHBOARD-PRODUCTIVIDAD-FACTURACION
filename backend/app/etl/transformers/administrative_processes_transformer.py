"""Administrative processes DataFrame transformers."""

import pandas as pd

from ..utils.dataframe_helpers import normalize_column_names

REQUIRED_PROCESS_COLUMNS = ("FECHA", "NOMBRE", "DOCUMENTO", "PROCESO", "CANTIDAD")
PROCESS_TEXT_COLUMNS = ("NOMBRE", "DOCUMENTO", "PROCESO")

ERROR_MISSING_PROCESS_COLUMNS = (
    "Missing required columns: {missing}. Available columns: {available}"
)


def _ensure_required_columns(df: pd.DataFrame, required_columns: tuple[str, ...]) -> None:
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(
            ERROR_MISSING_PROCESS_COLUMNS.format(
                missing=", ".join(missing),
                available=", ".join(df.columns.tolist()),
            )
        )


def process_administrative_processes(df: pd.DataFrame) -> pd.DataFrame | None:
    """Normalize, validate, type-cast and clean administrative process rows."""
    if df is None or df.empty:
        return None

    result_df = df.copy()

    first_row_upper = result_df.iloc[0].astype(str).str.upper()
    if "FECHA" in first_row_upper.values or "NOMBRE" in first_row_upper.values:
        result_df.columns = result_df.iloc[0].astype(str).str.strip().str.upper()
        result_df = result_df.iloc[1:].reset_index(drop=True)
    else:
        result_df = normalize_column_names(result_df)

    _ensure_required_columns(result_df, REQUIRED_PROCESS_COLUMNS)

    result_df = result_df.dropna(how="all")
    result_df["FECHA"] = pd.to_datetime(result_df["FECHA"], errors="coerce")
    result_df["CANTIDAD"] = pd.to_numeric(result_df["CANTIDAD"], errors="coerce")
    result_df = result_df.dropna(subset=["FECHA", "NOMBRE", "CANTIDAD"])

    for col in PROCESS_TEXT_COLUMNS:
        if col in result_df.columns:
            result_df[col] = result_df[col].astype(str).str.strip()

    return result_df
