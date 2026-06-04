"""
File Management Utilities
===================================
Auxiliary functions for reading, writing, and manipulating files.
"""

import pandas as pd
import os


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
        print(f"Error al guardar {filepath}: {e}")
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
        print(f"Error al cargar {filepath}: {e}")
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
    """
    try:
        if file.name.endswith('.csv'):
            df_raw = pd.read_csv(file, header=None)
        else:
            df_raw = pd.read_excel(file, header=None)

        header_row = detect_header_row(df_raw, column_marker)

        if header_row is None:
            return None, None

        file.seek(0)
        if file.name.endswith('.csv'):
            df = pd.read_csv(file, header=header_row)
        else:
            df = pd.read_excel(file, header=header_row)

        df = normalize_column_names(df)

        return df, header_row

    except Exception as e:
        print(f"Error al leer archivo: {e}")
        return None, None
