"""Excel and uploaded file loaders."""

import pandas as pd

from ..file_helpers import read_file_robust
REQUIRED_PROCESS_COLUMNS = ("FECHA", "NOMBRE", "DOCUMENTO", "PROCESO", "CANTIDAD")

ERROR_MISSING_PROCESS_COLUMNS = "Missing required process columns: {columns}"
ERROR_PROCESS_LOAD_FAILED = "Failed to load processes dataset: {error}"


def load_uploaded_dataframe(file, header_marker: str) -> pd.DataFrame | None:
    """Load uploaded file by auto-detecting real header row using marker."""
    df, _ = read_file_robust(file, header_marker)
    return df


