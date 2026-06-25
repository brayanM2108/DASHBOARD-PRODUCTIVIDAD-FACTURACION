"""
File Management Utilities
===================================
Auxiliary functions for reading, writing, and manipulating files.
"""

import logging
import os

import pandas as pd

logger = logging.getLogger(__name__)


def save_to_parquet(df, filepath):
    """
    Save a DataFrame in Parquet format.
    """
    if df is None or df.empty:
        return False

    try:
        df.astype(str).to_parquet(filepath, index=False)
        return True
    except Exception as e:
        logger.error("Error saving parquet %s: %s", filepath, e)
        return False


def load_from_parquet(filepath):
    """
    Load a DataFrame from a Parquet file.
    """
    if not os.path.exists(filepath):
        return None

    try:
        return pd.read_parquet(filepath)
    except Exception as e:
        logger.error("Error loading parquet %s: %s", filepath, e)
        return None


def detect_header_row(df_raw, column_marker):
    """
    Detects the header row in a DataFrame.

    Looks for a row containing the specified marker to identify where the actual headers begin.

    """
    for i, row in df_raw.iterrows():
        row_str = row.astype(str).str.strip().str.upper()
        if row_str.str.startswith(column_marker.upper()).any():
            return i
    return None


def normalize_column_names(df):
    """
    Normalizes column names in a DataFrame.

    Removes spaces, line breaks, and converts to uppercase.
    """
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.replace('\n', ' ')
        .str.upper()
    )
    return df


def read_file_robust(file, column_marker):
    """
    Reads a file robustly by automatically detecting headers.
    Reads the file only once — reuses the already-loaded DataFrame.
    """
    try:
        if file.name.endswith('.csv'):
            df_raw = pd.read_csv(file, header=None)
        else:
            df_raw = pd.read_excel(file, header=None)

        header_row = detect_header_row(df_raw, column_marker)

        if header_row is None:
            return None, None

        df_raw.columns = df_raw.iloc[header_row].astype(str)
        df = df_raw.iloc[header_row + 1:].reset_index(drop=True)
        df = df.dropna(axis=1, how='all')

        df = normalize_column_names(df)

        return df, header_row

    except Exception as e:
        logger.error("Error reading file: %s", e)
        return None, None
