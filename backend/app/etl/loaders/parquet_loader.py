"""Parquet persistence loaders."""

from collections.abc import Mapping

import pandas as pd

from ..file_helpers import load_from_parquet, save_to_parquet
from ...utils.config.settings import FILES

DATASET_TO_FILE_KEY = {
    "legalizations_df": "Legalizaciones",
    "billing_df": "Facturacion",
    "billers_df": "Facturadores",
    "electronic_billing_df": "FacturacionElectronica",
    "administrative_processes_df": "ArchivoProcesos",
}


def load_all_persisted_frames() -> dict[str, pd.DataFrame | None]:
    """Load all persisted parquet datasets using session-state friendly keys."""
    datasets: dict[str, pd.DataFrame | None] = {}
    for dataset_key, file_key in DATASET_TO_FILE_KEY.items():
        datasets[dataset_key] = load_from_parquet(FILES[file_key])
    return datasets


def load_all_persisted_frames_cached() -> dict[str, pd.DataFrame | None]:
    """Compatibility wrapper without framework-level caching."""
    return load_all_persisted_frames()


def save_all_persisted_frames(data_by_dataset: Mapping[str, pd.DataFrame]) -> dict[str, bool]:
    """Persist provided datasets as parquet using the unified file mapping."""
    results: dict[str, bool] = {}

    for dataset_key, df in data_by_dataset.items():
        file_key = DATASET_TO_FILE_KEY.get(dataset_key)
        if file_key is None:
            continue
        results[dataset_key] = save_to_parquet(df, FILES[file_key])

    return results


def persist_legalizations(df: pd.DataFrame) -> dict[str, bool]:
    """Persist the unified legalizations dataframe."""
    return save_all_persisted_frames({"legalizations_df": df})


def persist_administrative_processes(df: pd.DataFrame) -> dict[str, bool]:
    """Persist processed administrative processes dataframe using canonical key."""
    return save_all_persisted_frames({"administrative_processes_df": df})
