from __future__ import annotations

import os
from pathlib import Path
import sys

import pandas as pd
import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.etl.loaders.excel_loader import load_uploaded_dataframe
from app.services.legalizations_service import process_legalizations


DEFAULT_INFORME_PATH = Path(
    r"C:\Users\TECNICOESTADISTICO.P\Downloads\Informe_Legalizaciones_completo (62).xlsx"
)


class UploadedFile:
    def __init__(self, path: Path):
        self.path = path
        self.name = path.name
        self._handle = path.open("rb")

    def seek(self, offset: int, whence: int = 0):
        return self._handle.seek(offset, whence)

    def read(self, *args, **kwargs):
        return self._handle.read(*args, **kwargs)

    def close(self):
        return self._handle.close()

    def __getattr__(self, item):
        return getattr(self._handle, item)


def _normalize(text: str) -> str:
    return (
        str(text)
        .strip()
        .upper()
        .replace("Á", "A")
        .replace("É", "E")
        .replace("Í", "I")
        .replace("Ó", "O")
        .replace("Ú", "U")
        .replace("Ñ", "N")
    )


def test_informe_legalizaciones_loader_and_classification():
    path = Path(os.getenv("INFORME_LEGALIZACIONES_PATH", str(DEFAULT_INFORME_PATH)))

    if not path.exists():
        pytest.skip(f"Informe no encontrado en: {path}")

    uploaded = UploadedFile(path)
    try:
        df = load_uploaded_dataframe(uploaded, "ID_LEGALIZACION")
    finally:
        uploaded.close()

    assert df is not None, "El loader no pudo detectar el encabezado con ID_LEGALIZACION."

    required_columns = {"CONVENIO", "ESTADO", "FECHA_REAL", "USUARIO"}
    missing_columns = required_columns - set(df.columns)
    assert not missing_columns, f"Faltan columnas esperadas en el archivo: {sorted(missing_columns)}"

    result = process_legalizations(df)

    assert result["error"] is None, f"El proceso falló: {result['error']}"
    assert result["total_rows"] > 0, "No quedaron filas después del procesamiento."
    assert result["ppl_count"] > 0, "No se detectaron filas PPL."
    assert result["agreements_count"] > 0, "No se detectaron filas de Convenios."

    legalizations_df = result["legalizations_df"]
    assert legalizations_df is not None and not legalizations_df.empty, "El dataframe procesado quedó vacío."
    assert "LEGALIZATION_TYPE" in legalizations_df.columns, "No se agregó LEGALIZATION_TYPE."

    ppl_name = _normalize("Patrimonio Autonomo Fondo Atención Salud PPL 2024")
    convenio_normalized = legalizations_df["CONVENIO"].astype(str).map(_normalize)
    type_normalized = legalizations_df["LEGALIZATION_TYPE"].astype(str).str.strip().str.upper()

    expected_ppl = int((convenio_normalized == ppl_name).sum())
    expected_agreements = int((convenio_normalized != ppl_name).sum())

    assert result["ppl_count"] == expected_ppl, (
        f"Conteo PPL inesperado: {result['ppl_count']} != {expected_ppl}"
    )
    assert result["agreements_count"] == expected_agreements, (
        f"Conteo Convenios inesperado: {result['agreements_count']} != {expected_agreements}"
    )

    assert set(type_normalized.unique()) <= {"PPL", "AGREEMENT"}, (
        f"Valores inesperados en LEGALIZATION_TYPE: {sorted(set(type_normalized.unique()))}"
    )
