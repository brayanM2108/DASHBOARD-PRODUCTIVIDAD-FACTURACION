"""
Business logic - RIPS
=====================
Functions for RIPS processing and productivity analytics.
"""

import pandas as pd

from data.processors import (
    process_rips_data,
    merge_with_billers,
    aggregate_records_by_user,
    filter_by_billers,
)
from data.validators import (
    validate_rips_dataframe,
    find_first_column_variant,
)
from config.settings import COLUMN_NAMES
from utils.date_helpers import filter_by_date_range


# Centralized error messages.
ERROR_VALIDATION_FAILED = "RIPS validation failed"

def _build_process_error_result(message):
    """Standard error payload for RIPS processing."""
    return {
        "rips_df": None,
        "error": message,
    }

def _empty_productivity_metrics():
    """Standard metrics payload when input data is empty."""
    return {
        "total": 0,
        "by_user": None,
        "by_date": None,
        "daily_average": 0,
    }

def _is_user_filter_active(selected_users):
    """Return True when a specific user filter is active."""
    return (
            selected_users
            and "All" not in selected_users
            and "Todos" not in selected_users
            and len(selected_users) > 0
    )

def process_rips(df, billers_df=None):
    """
    Validate and process RIPS dataframe.
    """
    is_valid, message = validate_rips_dataframe(df)
    if not is_valid:
        return _build_process_error_result(f"{ERROR_VALIDATION_FAILED}: {message}")

    rips_df = process_rips_data(df)

    if billers_df is not None and rips_df is not None:
        user_col = find_first_column_variant(rips_df, COLUMN_NAMES["usuario"])
        if user_col:
            rips_df = merge_with_billers(rips_df, billers_df, user_col)

        # Convert biller document -> biller name.
        rips_df = map_document_to_name(rips_df, billers_df)

        # Filter after mapping (name-based comparison).
        user_col_post = find_first_column_variant(rips_df, COLUMN_NAMES["usuario"])
        rips_df = filter_by_billers(rips_df, billers_df, user_col_post, "NOMBRE")

    return {
        "rips_df": rips_df,
        "error": None,
    }

def filter_rips(df, start_date, end_date, selected_users=None):
    """
    Filter RIPS by date and users.
    """
    if df is None or df.empty:
        return df

    date_col = find_first_column_variant(df, COLUMN_NAMES["fecha"])
    if date_col is None:
        return df

    filtered_df = filter_by_date_range(df, date_col, start_date, end_date)

    if _is_user_filter_active(selected_users):
        user_col = find_first_column_variant(filtered_df, COLUMN_NAMES["usuario"])
        if user_col and user_col in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[user_col].isin(selected_users)]

    return filtered_df


def map_document_to_name(rips_df, billers_df):
    """
    Replace biller DOCUMENT value with NOMBRE in RIPS user column.
    """
    if rips_df is None or rips_df.empty:
        return rips_df

    if billers_df is None or billers_df.empty:
        return rips_df

    user_col = find_first_column_variant(rips_df, COLUMN_NAMES["usuario"])
    if user_col is None:
        return rips_df

    if "DOCUMENTO" not in billers_df.columns or "NOMBRE" not in billers_df.columns:
        return rips_df

    result_df = rips_df.copy()
    normalized_billers_df = billers_df.copy()

    normalized_billers_df["DOCUMENTO"] = (
        normalized_billers_df["DOCUMENTO"]
        .astype(str)
        .str.strip()
        .str.upper()
    )
    normalized_billers_df["NOMBRE"] = (
        normalized_billers_df["NOMBRE"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    document_to_name_map = (
        normalized_billers_df
        .dropna(subset=["DOCUMENTO", "NOMBRE"])
        .drop_duplicates(subset=["DOCUMENTO"])
        .set_index("DOCUMENTO")["NOMBRE"]
    )

    result_df[user_col] = (
        result_df[user_col]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    result_df[user_col] = result_df[user_col].map(document_to_name_map).fillna(result_df[user_col])

    return result_df


def calculate_rips_productivity(df):
    """
    Calculate RIPS productivity metrics.
    """
    if df is None or df.empty:
        return _empty_productivity_metrics()

    user_col = find_first_column_variant(df, COLUMN_NAMES["usuario"])
    date_col = find_first_column_variant(df, COLUMN_NAMES["fecha"])

    total = len(df)

    by_user = None
    if user_col:
        by_user = aggregate_records_by_user(df, user_col, date_col, group_by_date=False)

    by_date = None
    if date_col:
        temp_df = df.copy()
        temp_df["DATE"] = pd.to_datetime(temp_df[date_col]).dt.date
        by_date = temp_df.groupby("DATE").size().reset_index(name="COUNT")

    daily_average = 0
    if by_date is not None and not by_date.empty:
        daily_average = by_date["COUNT"].mean()

    return {
        "total": total,
        "by_user": by_user,
        "by_date": by_date,
        "daily_average": daily_average,
    }
