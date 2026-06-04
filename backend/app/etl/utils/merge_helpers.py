"""Reusable merge helpers for ETL transformations."""

import pandas as pd

from .dataframe_helpers import normalize_object_columns_in_place, normalize_text_series

COMPARISON_MODE_DOCUMENT = "DOCUMENTO"
COMPARISON_MODE_NAME = "NOMBRE"


def merge_with_billers(
    df: pd.DataFrame,
    billers_df: pd.DataFrame,
    user_column: str = "USUARIO",
) -> pd.DataFrame:
    """Left-merge dataframe with billers master info."""
    if df is None or df.empty or billers_df is None or billers_df.empty:
        return df

    if user_column not in df.columns or "USUARIO" not in billers_df.columns:
        return df

    return pd.merge(df, billers_df, left_on=user_column, right_on="USUARIO", how="left")


def merge_billing_with_electronic_billing(
    billing_df: pd.DataFrame,
    electronic_billing_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Assign user to billing records by matching:
    billing.NRO_FACTURACLI -> electronic_billing.FACTURA
    """
    if billing_df is None or billing_df.empty:
        return billing_df

    if electronic_billing_df is None or electronic_billing_df.empty:
        return billing_df

    result_df = billing_df.copy()
    normalized_e_billing_df = electronic_billing_df.copy()

    normalize_object_columns_in_place(result_df)
    normalize_object_columns_in_place(normalized_e_billing_df)

    state_col = "ESTADO" if "ESTADO" in normalized_e_billing_df.columns else "Estado"
    if state_col in normalized_e_billing_df.columns:
        active_e_billing_df = normalized_e_billing_df[
            normalized_e_billing_df[state_col] == "ACTIVO"
        ].copy()
    else:
        active_e_billing_df = normalized_e_billing_df.copy()

    if "FACTURA" in active_e_billing_df.columns and "USUARIO" in active_e_billing_df.columns:
        user_map = (
            active_e_billing_df
            .dropna(subset=["FACTURA", "USUARIO"])
            .drop_duplicates(subset=["FACTURA"])
            .set_index("FACTURA")["USUARIO"]
        )

        if "NRO_FACTURACLI" in result_df.columns:
            result_df["USUARIO"] = result_df["NRO_FACTURACLI"].map(user_map)

    return result_df


def filter_by_billers(
    df: pd.DataFrame,
    billers_df: pd.DataFrame,
    user_column: str,
    comparison_mode: str = COMPARISON_MODE_DOCUMENT,
) -> pd.DataFrame:
    """Keep only rows where user value exists in billers master comparison column."""
    if df is None or df.empty:
        return df
    if billers_df is None or billers_df.empty:
        return df
    if user_column is None or user_column not in df.columns:
        return df
    if comparison_mode not in billers_df.columns:
        return df

    valid_values = (
        billers_df[comparison_mode]
        .dropna()
        .astype(str)
        .str.strip()
        .str.upper()
        .unique()
        .tolist()
    )

    result_df = df.copy()
    result_df["_user_norm"] = normalize_text_series(result_df[user_column])
    filtered_df = result_df[result_df["_user_norm"].isin(valid_values)].copy()
    return filtered_df.drop(columns=["_user_norm"])
