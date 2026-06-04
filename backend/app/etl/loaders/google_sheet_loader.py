"""Google Sheets loaders."""

import re
from typing import Any

import pandas as pd


def build_google_sheets_export_url(file_or_url: Any) -> Any:
    """Convert a Google Sheets edit URL into an Excel export URL."""
    if not isinstance(file_or_url, str):
        return file_or_url

    if "docs.google.com/spreadsheets" not in file_or_url:
        return file_or_url

    if "/edit" in file_or_url and "/d/" in file_or_url:
        sheet_id = file_or_url.split("/d/")[1].split("/")[0]
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"

    return file_or_url


def extract_google_sheet_ids(sheet_url: str) -> tuple[str | None, str]:
    """Extract sheet_id and gid from a Google Sheets URL."""
    if not isinstance(sheet_url, str) or not sheet_url.strip():
        return None, "0"

    id_match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", sheet_url)
    if not id_match:
        return None, "0"

    gid = "0"
    gid_match = re.search(r"[#&]gid=([0-9]+)", sheet_url)
    if gid_match:
        gid = gid_match.group(1)

    return id_match.group(1), gid


def build_google_sheet_csv_url(sheet_id: str, gid: str = "0") -> str:
    """Build CSV export URL from sheet_id and gid."""
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


def load_google_sheet_csv(sheet_url: str) -> pd.DataFrame:
    """Load raw dataframe from Google Sheets using CSV export endpoint."""
    sheet_id, gid = extract_google_sheet_ids(sheet_url)
    if not sheet_id:
        raise ValueError("Could not extract Google Sheet ID from URL.")

    csv_url = build_google_sheet_csv_url(sheet_id, gid)
    return pd.read_csv(csv_url)

