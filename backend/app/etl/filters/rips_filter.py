from ..utils.date_helpers import filter_by_date_range
from ..validators import find_first_column_variant
from ...utils.config.settings import COLUMN_NAMES_RIPS


def filter_rips(df, start_date, end_date, selected_users=None):
    if df is None or df.empty:
        return df

    filtered_df = df

    if start_date is None or end_date is None:
        return filtered_df

    date_col = find_first_column_variant(filtered_df, COLUMN_NAMES_RIPS["fecha"])
    if date_col is None:
        return filtered_df

    filtered_df = filter_by_date_range(filtered_df, date_col, start_date, end_date)

    if selected_users and "All" not in selected_users and "Todos" not in selected_users and len(selected_users) > 0:
        user_col = find_first_column_variant(filtered_df, COLUMN_NAMES_RIPS["usuario"])
        if user_col and user_col in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[user_col].isin(selected_users)]

    return filtered_df
