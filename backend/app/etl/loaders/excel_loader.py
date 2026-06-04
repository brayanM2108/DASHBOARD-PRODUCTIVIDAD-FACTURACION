"""Excel and uploaded file loaders."""

from typing import Any

import pandas as pd

from ..file_helpers import read_file_robust
from .google_sheet_loader import build_google_sheets_export_url
from ..utils.dataframe_helpers import normalize_columns_upper_in_place

REQUIRED_PROCESS_COLUMNS = ("FECHA", "NOMBRE", "DOCUMENTO", "PROCESO", "CANTIDAD")

ERROR_MISSING_PROCESS_COLUMNS = "Missing required process columns: {columns}"
ERROR_PROCESS_LOAD_FAILED = "Failed to load processes dataset: {error}"


def load_uploaded_dataframe(file, header_marker: str) -> pd.DataFrame | None:
    """Load uploaded file by auto-detecting real header row using marker."""
    df, _ = read_file_robust(file, header_marker)
    return df


def load_processes_data(file_or_url: Any) -> pd.DataFrame:
    """Load administrative processes data from uploaded Excel file or Google Sheets URL."""
    try:
        source = build_google_sheets_export_url(file_or_url)
        df = pd.read_excel(source)
        df = normalize_columns_upper_in_place(df)

        missing = [col for col in REQUIRED_PROCESS_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(ERROR_MISSING_PROCESS_COLUMNS.format(columns=", ".join(missing)))

        df["FECHA"] = pd.to_datetime(df["FECHA"], format="%d/%m/%Y", errors="coerce")
        df["CANTIDAD"] = pd.to_numeric(df["CANTIDAD"], errors="coerce")

        return df.dropna(subset=["FECHA", "NOMBRE", "CANTIDAD"])

    except Exception as exc:
        raise ValueError(ERROR_PROCESS_LOAD_FAILED.format(error=str(exc))) from exc
