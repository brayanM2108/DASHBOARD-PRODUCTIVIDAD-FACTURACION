import os
from pathlib import Path
import sys

import pandas as pd
import pytest

# Ensure backend/app is importable when running from repo root.
BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.etl.utils.dataframe_helpers import normalize_text_series
from app.utils.config.settings import FILES, VALID_STATES_LEGALIZATIONS


def _load_legalizations_parquet() -> Path:
    parquet_path = os.getenv("LEGALIZATIONS_PARQUET") or FILES["Legalizaciones"]
    raw_path = Path(parquet_path)
    candidates = [raw_path]

    if not raw_path.is_absolute():
        repo_root = BACKEND_ROOT.parent
        candidates.append(repo_root / raw_path)
        candidates.append(BACKEND_ROOT / raw_path)

    for candidate in candidates:
        if candidate.exists():
            return candidate

    tried = ", ".join(str(p) for p in candidates)
    pytest.skip(f"legalizations.parquet not found. Tried: {tried}")


def test_legalizations_type_column_presence():
    path = _load_legalizations_parquet()
    df = pd.read_parquet(path)

    assert "CONVENIO" in df.columns, "Missing CONVENIO column in legalizations parquet."
    if "LEGALIZATION_TYPE" not in df.columns:
        pytest.skip("LEGITIMACY: legacy parquet detected without LEGALIZATION_TYPE; load the unified file to run this test.")

    if "ESTADO" in df.columns:
        estado_norm = normalize_text_series(df["ESTADO"])
        df = df[estado_norm.isin([s.upper() for s in VALID_STATES_LEGALIZATIONS])]

    type_norm = normalize_text_series(df["LEGALIZATION_TYPE"])
    type_values = set(type_norm.unique())

    assert "PPL" in type_values, "Missing PPL rows in LEGALIZATION_TYPE."
    assert "AGREEMENT" in type_values, "Missing AGREEMENT rows in LEGALIZATION_TYPE."

    ppl_df = df[type_norm == "PPL"]
    agreements_df = df[type_norm == "AGREEMENT"]

    msg = (
        f"Total rows after filters: {len(df)} | "
        f"PPL rows: {len(ppl_df)} | Agreements rows: {len(agreements_df)}"
    )

    assert len(agreements_df) > 0, msg
    assert len(ppl_df) > 0, msg
