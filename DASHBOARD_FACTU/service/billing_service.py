"""
Business logic - Billing
========================
Functions for billing data processing and analytics.
"""

import pandas as pd

from data.processors import (
    aggregate_records_by_user,
    filter_by_billers,
    merge_billing_with_electronic_billing,
    merge_with_billers,
    process_billing_data,
)

from data.validators import (
    find_first_column_variant ,
    validate_billing_dataframe,
)

from config.settings import COLUMN_NAMES
from utils.date_helpers import filter_by_date_range


# Centralized error messages.
ERROR_NO_BILLING_DATA = "No billing data available"
ERROR_NO_E_BILLING_DATA = "No electronic billing data available"
ERROR_USER_NOT_DETERMINED = "Could not determine user column"
ERROR_NO_MATCHES_FOUND = "No matches found"
ERROR_NO_VALID_AREA_USERS = "No valid users from the area"

def _build_error_result(message):
    """Standard error payload for billing-user merge operations."""
    return {
        "billing_with_user_df": None,
        "billing_by_user_df": None,
        "user_column": None,
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
    """Return True when a specific user filter is actually active."""
    return (
            selected_users
            and "All" not in selected_users
            and "Todos" not in selected_users
            and len(selected_users) > 0
    )

def _normalize_text_key(value) -> str | None:
    """Normalize text values for matching by name."""
    if pd.isna(value):
        return None

    text = str(value).strip().upper()
    if text in {"", "NAN", "NONE"}:
        return None

    return text


def _normalize_document_key(value) -> str | None:
    """Normalize document values for stable matching."""
    if pd.isna(value):
        return None

    text = str(value).strip().upper()
    if text in {"", "NAN", "NONE"}:
        return None

    # Frequent Excel artifact: numeric IDs loaded as '<id>.0'
    if text.endswith(".0"):
        text = text[:-2]

    # Keep only alphanumeric chars (remove spaces, dashes, dots, etc.)
    text = "".join(ch for ch in text if ch.isalnum())
    return text or None



def process_billing(df, billers_df=None):
    """Validate and process billing dataframe."""
    is_valid, message = validate_billing_dataframe(df)
    if not is_valid:
        return {"error": message, "billing_df": None}

    billing_df = process_billing_data(df)

    if billers_df is not None and billing_df is not None:
        user_col = find_first_column_variant(billing_df, COLUMN_NAMES["usuario"])
        if user_col:
            billing_df = merge_with_billers(billing_df, billers_df, user_col)

    return {
        "billing_df": billing_df,
        "error": None,
    }

def filter_billing(df, start_date, end_date, selected_users=None):
    """Filter billing dataframe by date range and optional user selection."""
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

def get_billing_with_user(billing_df, electronic_billing_df, billers_df=None):
    """
    Merge billing data with electronic billing data to assign users.
    Optionally filter users against the official billers master dataset.
    """
    if billing_df is None or billing_df.empty:
        return _build_error_result(ERROR_NO_BILLING_DATA)

    if electronic_billing_df is None or electronic_billing_df.empty:
        return _build_error_result(ERROR_NO_E_BILLING_DATA)

    billing_with_user_df = merge_billing_with_electronic_billing(billing_df, electronic_billing_df)

    user_col = find_first_column_variant(billing_with_user_df, COLUMN_NAMES["usuario"])
    if user_col is None or user_col not in billing_with_user_df.columns:
        return _build_error_result(ERROR_USER_NOT_DETERMINED)

    valid_user_rows_df = billing_with_user_df[billing_with_user_df[user_col].notna()].copy()
    if valid_user_rows_df.empty:
        return _build_error_result(ERROR_NO_MATCHES_FOUND)

    if billers_df is not None and not billers_df.empty:
        has_doc = "DOCUMENTO" in billers_df.columns
        has_name = "NOMBRE" in billers_df.columns

        # Compare real overlap against master by both strategies
        users_name = {
            x for x in valid_user_rows_df[user_col].map(_normalize_text_key).dropna().unique().tolist()
        }
        users_doc = {
            x for x in valid_user_rows_df[user_col].map(_normalize_document_key).dropna().unique().tolist()
        }

        billers_names = set()
        billers_docs = set()

        if has_name:
            billers_names = {
                x for x in billers_df["NOMBRE"].map(_normalize_text_key).dropna().unique().tolist()
            }

        if has_doc:
            billers_docs = {
                x for x in billers_df["DOCUMENTO"].map(_normalize_document_key).dropna().unique().tolist()
            }

        name_hits = len(users_name & billers_names)
        doc_hits = len(users_doc & billers_docs)

        # Choose the mode with better real match
        comparison_mode = "DOCUMENTO" if (has_doc and doc_hits > name_hits) else "NOMBRE"

        if comparison_mode == "DOCUMENTO" and has_doc:
            users_tmp = valid_user_rows_df.copy()
            billers_tmp = billers_df.copy()

            users_tmp[user_col] = users_tmp[user_col].map(_normalize_document_key)
            billers_tmp["DOCUMENTO"] = billers_tmp["DOCUMENTO"].map(_normalize_document_key)

            valid_user_rows_df = filter_by_billers(
                users_tmp,
                billers_tmp,
                user_col,
                "DOCUMENTO",
            )
        elif has_name:
            valid_user_rows_df = filter_by_billers(
                valid_user_rows_df,
                billers_df,
                user_col,
                "NOMBRE",
            )

    if valid_user_rows_df.empty:
        return _build_error_result(ERROR_NO_VALID_AREA_USERS)

    billing_by_user_df = (
        valid_user_rows_df
        .groupby(user_col)
        .size()
        .reset_index(name="COUNT")
    )

    if billers_df is not None and not billers_df.empty:
        billing_by_user_df = merge_with_billers(billing_by_user_df, billers_df, user_col)

    billing_by_user_df = billing_by_user_df.sort_values("COUNT", ascending=False)

    return {
        "billing_with_user_df": valid_user_rows_df,
        "billing_by_user_df": billing_by_user_df,
        "user_column": user_col,
        "error": None,
    }


def calculate_billing_productivity(df):
    """Calculate billing productivity metrics."""
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
