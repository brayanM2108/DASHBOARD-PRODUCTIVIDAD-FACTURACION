"""
Business logic - Billing (Electronic-only)
==========================================
Productivity calculations based only on electronic billing data.
No cross-merge with manual billing and no matching against billers master.
"""

import pandas as pd

from data.validators import find_first_column_variant
from config.settings import COLUMN_NAMES_BILLING
from utils.date_helpers import filter_by_date_range


# Centralized error messages.
ERROR_NO_E_BILLING_DATA = "No electronic billing data available"
ERROR_USER_NOT_DETERMINED = "Could not determine user column"
ERROR_NO_MATCHES_FOUND = "No matches found"

# Canonical columns for electronic billing productivity.
USER_COLUMN = "USUARIO"
VALUE_COLUMN = "VALOR TERCERO"


def _build_error_result(message):
    """Standard error payload for billing-user operations."""
    return {
        "billing_with_user_df": None,
        "billing_by_user_df": None,
        "user_column": None,
        "error": message,
    }


def _empty_productivity_metrics():
    """Standard metrics payload when input data is empty."""
    return {
        # Legacy fields (compatibilidad con report_service / excel_exporter)
        "total": 0,
        "by_user": None,
        "by_date": None,
        "daily_average": 0,
        # Nuevos campos duales
        "total_records": 0,
        "total_valor_tercero": 0.0,
        "by_user_dual": None,
        "by_date_dual": None,
        "daily_avg_records": 0.0,
        "daily_avg_valor_tercero": 0.0,
    }


def _is_user_filter_active(selected_users):
    """Return True when a specific user filter is actually active."""
    return (
            selected_users
            and "All" not in selected_users
            and "Todos" not in selected_users
            and len(selected_users) > 0
    )


def _normalize_user_series(series: pd.Series) -> pd.Series:
    """Normalize user values for stable filtering/grouping."""
    return series.astype(str).str.strip()


def _parse_amount_series(series: pd.Series) -> pd.Series:
    """
    Convert amount values to numeric.
    Handles common formatting artifacts: thousands separators and commas.
    """
    cleaned = (
        series.astype(str)
        .str.strip()
        .str.replace(r"[^\d,\.\-]", "", regex=True)
        .str.replace(",", "", regex=False)
    )
    return pd.to_numeric(cleaned, errors="coerce").fillna(0.0)


def _find_user_column(df: pd.DataFrame) -> str | None:
    return find_first_column_variant(df, COLUMN_NAMES_BILLING.get("usuario", []))


def _find_date_column(df: pd.DataFrame) -> str | None:
    return find_first_column_variant(df, COLUMN_NAMES_BILLING.get("fecha", []))


def _prepare_electronic_billing_df(df: pd.DataFrame | None) -> pd.DataFrame | None:
    """Standard cleanup for electronic billing productivity calculations."""
    if df is None or df.empty:
        return None

    result_df = df.copy()
    result_df.columns = result_df.columns.astype(str).str.strip().str.upper()

    user_col = _find_user_column(result_df)
    if user_col is None or user_col not in result_df.columns:
        return None
    if VALUE_COLUMN not in result_df.columns:
        return None

    result_df[user_col] = _normalize_user_series(result_df[user_col])
    result_df = result_df[result_df[user_col].notna()]
    result_df = result_df[result_df[user_col] != ""]

    result_df[VALUE_COLUMN] = _parse_amount_series(result_df[VALUE_COLUMN])

    date_col = _find_date_column(result_df)
    if date_col:
        result_df[date_col] = pd.to_datetime(result_df[date_col], errors="coerce")

    return result_df


def process_billing(df, billers_df=None):
    """
    Process billing dataframe as electronic billing source.
    billers_df is ignored intentionally (no master matching required).
    """
    _ = billers_df  # backward-compatible signature

    if df is None or df.empty:
        return {"error": ERROR_NO_E_BILLING_DATA, "billing_df": None}

    prepared_df = _prepare_electronic_billing_df(df)
    if prepared_df is None:
        return {"error": ERROR_USER_NOT_DETERMINED, "billing_df": None}

    return {
        "billing_df": prepared_df,
        "error": None,
    }


def filter_billing(df, start_date, end_date, selected_users=None):
    """Filter electronic billing dataframe by date range and optional user selection."""
    if df is None or df.empty:
        return df

    prepared_df = _prepare_electronic_billing_df(df)
    if prepared_df is None or prepared_df.empty:
        return prepared_df

    user_col = _find_user_column(prepared_df)
    date_col = _find_date_column(prepared_df)

    filtered_df = prepared_df
    if date_col is not None:
        filtered_df = filter_by_date_range(filtered_df, date_col, start_date, end_date)

    if _is_user_filter_active(selected_users) and user_col and user_col in filtered_df.columns:
        selected_set = {str(u).strip() for u in selected_users}
        filtered_df = filtered_df[filtered_df[user_col].isin(selected_set)]

    return filtered_df


def get_billing_with_user(billing_df, electronic_billing_df, billers_df=None):
    """
    Build productivity base only from electronic billing.
    - Uses USER directly as facturador.
    - Uses VALOR TERCERO for monetary aggregation.
    - No cross-merge and no billers master filtering.
    """
    _ = billing_df
    _ = billers_df

    if electronic_billing_df is None or electronic_billing_df.empty:
        return _build_error_result(ERROR_NO_E_BILLING_DATA)

    prepared_df = _prepare_electronic_billing_df(electronic_billing_df)
    if prepared_df is None or prepared_df.empty:
        return _build_error_result(ERROR_USER_NOT_DETERMINED)

    user_col = _find_user_column(prepared_df)
    if user_col is None:
        return _build_error_result(ERROR_USER_NOT_DETERMINED)

    valid_user_rows_df = prepared_df[prepared_df[user_col].notna()].copy()
    if valid_user_rows_df.empty:
        return _build_error_result(ERROR_NO_MATCHES_FOUND)

    # Mantiene COUNT como suma de valor para compatibilidad con reporte actual.
    billing_by_user_df = (
        valid_user_rows_df
        .groupby(user_col, as_index=False)[VALUE_COLUMN]
        .sum()
        .rename(columns={VALUE_COLUMN: "COUNT"})
        .sort_values("COUNT", ascending=False)
    )

    return {
        "billing_with_user_df": valid_user_rows_df,
        "billing_by_user_df": billing_by_user_df,
        "user_column": user_col,
        "error": None,
    }


def calculate_billing_productivity(df):
    """
    Calculate electronic billing productivity with dual metrics:
    - REGISTROS (count of rows)
    - VALOR_TERCERO (sum of billed value)

    Legacy compatibility:
    - total / by_user / by_date / daily_average remain available
      and are based on VALOR TERCERO.
    """
    prepared_df = _prepare_electronic_billing_df(df)
    if prepared_df is None or prepared_df.empty:
        return _empty_productivity_metrics()

    user_col = _find_user_column(prepared_df)
    date_col = _find_date_column(prepared_df)

    total_records = int(len(prepared_df))
    total_valor = float(prepared_df[VALUE_COLUMN].sum())

    by_user_dual = None
    by_user_legacy = None
    if user_col:
        by_user_dual = (
            prepared_df
            .groupby(user_col, as_index=False)
            .agg(
                REGISTROS=(user_col, "size"),
                VALOR_TERCERO=(VALUE_COLUMN, "sum"),
            )
            .sort_values("VALOR_TERCERO", ascending=False)
        )

        by_user_legacy = (
            by_user_dual[[user_col, "VALOR_TERCERO"]]
            .rename(columns={"VALOR_TERCERO": "COUNT"})
            .sort_values("COUNT", ascending=False)
        )

    by_date_dual = None
    by_date_legacy = None
    if date_col:
        temp_df = prepared_df.dropna(subset=[date_col]).copy()
        temp_df["DATE"] = pd.to_datetime(temp_df[date_col], errors="coerce").dt.date
        temp_df = temp_df.dropna(subset=["DATE"])

        by_date_dual = (
            temp_df
            .groupby("DATE", as_index=False)
            .agg(
                REGISTROS=(user_col, "size"),
                VALOR_TERCERO=(VALUE_COLUMN, "sum"),
            )
            .sort_values("DATE")
        )

        by_date_legacy = (
            by_date_dual[["DATE", "VALOR_TERCERO"]]
            .rename(columns={"VALOR_TERCERO": "COUNT"})
            .sort_values("DATE")
        )

    daily_avg_records = 0.0
    daily_avg_valor = 0.0
    if by_date_dual is not None and not by_date_dual.empty:
        daily_avg_records = float(by_date_dual["REGISTROS"].mean())
        daily_avg_valor = float(by_date_dual["VALOR_TERCERO"].mean())

    return {
        # Legacy (valor) for current report pipeline.
        "total": total_valor,
        "by_user": by_user_legacy,
        "by_date": by_date_legacy,
        "daily_average": daily_avg_valor,
        # New dual metrics.
        "total_records": total_records,
        "total_valor_tercero": total_valor,
        "by_user_dual": by_user_dual,
        "by_date_dual": by_date_dual,
        "daily_avg_records": daily_avg_records,
        "daily_avg_valor_tercero": daily_avg_valor,
    }
