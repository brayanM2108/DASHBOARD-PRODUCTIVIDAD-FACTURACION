"""Reusable merge helpers for ETL transformations."""

import pandas as pd

from .dataframe_helpers import normalize_object_columns_in_place, normalize_text_series

COMPARISON_MODE_DOCUMENT = "DOCUMENTO"
COMPARISON_MODE_NAME = "NOMBRE"


def merge_with_billers(
    df: pd.DataFrame,
    billers_df: pd.DataFrame,
    document_column: str = "NUMERO_IDENTIFICACION",
) -> pd.DataFrame:
    """
    Left-merge dataframe with billers master info using DOCUMENTO as key.
    Adds NOMBRE_USUARIO (official name) and TIPO_USUARIO (ROL) from billers.
    """
    if df is None or df.empty or billers_df is None or billers_df.empty:
        return df

    if document_column not in df.columns or "DOCUMENTO" not in billers_df.columns:
        return df

    result = df.merge(
        billers_df[["DOCUMENTO", "NOMBRE", "ROL"]].rename(
            columns={
                "DOCUMENTO": document_column,
                "NOMBRE": "NOMBRE_USUARIO",
                "ROL": "TIPO_USUARIO",
            }
        ),
        on=document_column,
        how="left",
    )

    return result


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
    document_column: str,
    comparison_mode: str = COMPARISON_MODE_DOCUMENT,
) -> pd.DataFrame:
    """
    Keep only rows where document value exists in billers master.
    Also adds NOMBRE_USUARIO (official name) from billers for display.
    """
    if df is None or df.empty:
        return df
    if billers_df is None or billers_df.empty:
        return df
    if document_column is None or document_column not in df.columns:
        return df
    if comparison_mode not in billers_df.columns:
        return df

    valid_values = set(
        billers_df[comparison_mode]
        .dropna()
        .astype(str)
        .str.strip()
        .str.upper()
        .unique()
    )

    result_df = df.copy()
    result_df["_doc_norm"] = normalize_text_series(result_df[document_column])
    filtered_df = result_df[result_df["_doc_norm"].isin(valid_values)].copy()

    billers_map = (
        billers_df[["DOCUMENTO", "NOMBRE"]]
        .dropna(subset=["DOCUMENTO"])
        .copy()
    )
    billers_map["_doc_key"] = normalize_text_series(billers_map["DOCUMENTO"])
    billers_map = billers_map.drop_duplicates(subset=["_doc_key"])

    filtered_df = filtered_df.merge(
        billers_map[["_doc_key", "NOMBRE"]].rename(columns={"NOMBRE": "NOMBRE_USUARIO"}),
        on="_doc_key",
        how="left",
    ).drop(columns=["_doc_norm", "_doc_key"])

    return filtered_df
