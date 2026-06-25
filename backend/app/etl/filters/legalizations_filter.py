import pandas as pd

from ..utils.date_helpers import filter_by_date_range
from ..validators import find_first_column_variant
from ...utils.config.settings import COLUMN_NAMES, COLUMN_NAMES_LEGALIZATIONS
from ..transformers.legalizations_transformer import LEGALIZATION_TYPE_COLUMN


def _is_user_filter_active(selected_users):
    return (
            selected_users
            and "All" not in selected_users
            and "Todos" not in selected_users
            and len(selected_users) > 0
    )


def _normalized_selector(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.upper()


def validate_users_exist(df: pd.DataFrame, selected_users: list[str]) -> list[str]:
    """Return list of selected users that do NOT exist in the dataframe."""
    if not _is_user_filter_active(selected_users):
        return []
    normalized_sel = [str(u).strip().upper() for u in selected_users]
    present = set()
    if "NOMBRE_USUARIO" in df.columns:
        present.update(_normalized_selector(df["NOMBRE_USUARIO"]).unique())
    user_col = find_first_column_variant(df, COLUMN_NAMES_LEGALIZATIONS["usuario"])
    if user_col and user_col in df.columns:
        present.update(_normalized_selector(df[user_col]).unique())
    return [u for u in selected_users if str(u).strip().upper() not in present]


def filter_legalizations(df, start_date, end_date, selected_users=None, legalization_type: str | None = None):
    """Filter legalizations by date range and optional user selection."""
    if df is None or df.empty:
        return df

    filtered_df = df

    if legalization_type and LEGALIZATION_TYPE_COLUMN in filtered_df.columns:
        filtered_df = filtered_df[filtered_df[LEGALIZATION_TYPE_COLUMN] == legalization_type]

    if start_date is None or end_date is None:
        return filtered_df

    date_col = find_first_column_variant(filtered_df, list(COLUMN_NAMES["fecha"]) + ["FECHA REAL"])
    if date_col is None:
        return filtered_df

    filtered_df = filter_by_date_range(filtered_df, date_col, start_date, end_date)

    if _is_user_filter_active(selected_users):
        normalized_sel = [str(u).strip().upper() for u in selected_users]
        mask = pd.Series(False, index=filtered_df.index)
        if "NOMBRE_USUARIO" in filtered_df.columns:
            mask = mask | _normalized_selector(filtered_df["NOMBRE_USUARIO"]).isin(normalized_sel)
        user_col = find_first_column_variant(filtered_df, COLUMN_NAMES_LEGALIZATIONS["usuario"])
        if user_col and user_col in filtered_df.columns:
            mask = mask | _normalized_selector(filtered_df[user_col]).isin(normalized_sel)
        filtered_df = filtered_df[mask]

    return filtered_df

