"""Reusable DataFrame normalization helpers."""

import pandas as pd


def normalize_text_series(series: pd.Series) -> pd.Series:
    """Normalize text values for stable matching."""
    return series.astype(str).str.strip().str.upper()


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with stripped uppercase column names."""
    df_copy = df.copy()
    df_copy.columns = df_copy.columns.astype(str).str.strip().str.upper()
    return df_copy


def normalize_object_columns_in_place(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize all object columns in place."""
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = normalize_text_series(df[col])
    return df


def normalize_columns_upper_in_place(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize dataframe columns to stripped uppercase in place."""
    df.columns = df.columns.astype(str).str.strip().str.upper()
    return df

