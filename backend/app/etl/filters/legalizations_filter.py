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
        user_col = find_first_column_variant(filtered_df, COLUMN_NAMES_LEGALIZATIONS["usuario"])
        if user_col and user_col in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[user_col].isin(selected_users)]

    return filtered_df

