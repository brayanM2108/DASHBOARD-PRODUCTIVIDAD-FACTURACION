"""
ETL - Electronic Billing Filters
=================================
Filtering operations for electronic billing DataFrames.
"""

import pandas as pd

from ..utils.date_helpers import filter_by_date_range
from ..validators import find_first_column_variant
from ...utils.config.settings import COLUMN_NAMES_BILLING


def _is_filter_active(selected_values):
    """Check if a multi-value filter is active (not All/Todos/None)."""
    if selected_values is None:
        return False
    if isinstance(selected_values, str):
        value = selected_values.strip()
        return bool(value and value not in {"All", "Todos"})
    if isinstance(selected_values, (list, tuple, set)):
        cleaned = [str(v).strip() for v in selected_values if str(v).strip()]
        return bool(cleaned and "All" not in cleaned and "Todos" not in cleaned)
    return False


def _find_column(df: pd.DataFrame, variants_key: str):
    """Find a column in billing df using COLUMN_NAMES_BILLING variants."""
    variants = COLUMN_NAMES_BILLING.get(variants_key, [])
    return find_first_column_variant(df, variants)


def filter_electronic_billing(
    df: pd.DataFrame,
    start_date,
    end_date,
    selected_users=None,
    selected_agreement=None,
    user_column: str | None = None,
    date_column: str | None = None,
    agreement_column: str | None = None,
) -> pd.DataFrame:
    """Filter electronic billing dataframe by date range, user and agreement."""
    if df is None or df.empty:
        return df

    user_col = user_column or _find_column(df, "usuario")
    date_col = date_column or _find_column(df, "fecha")
    agreement_col = agreement_column or _find_column(df, "convenio")

    filtered_df = df

    if date_col is not None:
        filtered_df = filter_by_date_range(filtered_df, date_col, start_date, end_date)

    if _is_filter_active(selected_users) and user_col and user_col in filtered_df.columns:
        selected_set = {str(u).strip() for u in selected_users}
        filtered_df = filtered_df[filtered_df[user_col].isin(selected_set)]

    if _is_filter_active(selected_agreement) and agreement_col and agreement_col in filtered_df.columns:
        if isinstance(selected_agreement, str):
            selected_set = {selected_agreement.strip()}
        else:
            selected_set = {str(v).strip() for v in selected_agreement}
        filtered_df = filtered_df[filtered_df[agreement_col].astype(str).str.strip().isin(selected_set)]

    return filtered_df


def filter_electronic_billing_by_agreement(df: pd.DataFrame, agreement_id) -> pd.DataFrame:
    """Filter electronic billing by agreement only."""
    if df is None or df.empty:
        return df

    agreement_col = _find_column(df, "convenio")
    if agreement_col is None:
        return df

    if not _is_filter_active(agreement_id):
        return df

    selected_set = {agreement_id.strip()} if isinstance(agreement_id, str) else {str(v).strip() for v in agreement_id}
    return df[df[agreement_col].astype(str).str.strip().isin(selected_set)]
