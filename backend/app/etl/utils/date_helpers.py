"""Reusable date helpers for ETL transformations."""

import datetime

import pandas as pd


def parse_date_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Convert a column to datetime format when present."""
    if column_name not in df.columns:
        return df

    df[column_name] = pd.to_datetime(df[column_name], errors="coerce")
    return df


def filter_by_date_range(df: pd.DataFrame, date_column: str, start_date, end_date) -> pd.DataFrame:
    """Filter a DataFrame by inclusive date range."""
    if date_column not in df.columns:
        return df

    result_df = df.copy()
    result_df[date_column] = pd.to_datetime(result_df[date_column], errors="coerce")
    result_df = result_df.dropna(subset=[date_column])

    mask = (result_df[date_column].dt.date >= start_date) & (result_df[date_column].dt.date <= end_date)
    return result_df[mask]


def get_default_date_range(days_back: int = 30):
    """Return a default date range ending today."""
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days_back)
    return start_date, end_date

