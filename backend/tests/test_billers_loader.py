from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.etl.loaders.billers_loader import load_billers_master
from app.utils.config.settings import FACTURADORES_FILE
from app.services.billers_service import get_billers_list


def test_facturadores_excel_loads_and_populates_billers_list():
    assert Path(FACTURADORES_FILE).exists(), f"No existe el archivo de facturadores: {FACTURADORES_FILE}"

    billers_df = load_billers_master()
    assert billers_df is not None, "El loader de facturadores devolvió None."
    assert not billers_df.empty, "El Excel de facturadores se cargó vacío."
    assert "NOMBRE" in billers_df.columns, "Falta la columna NOMBRE en el archivo de facturadores."

    billers_list = get_billers_list(billers_df)
    assert billers_list, "La lista de facturadores quedó vacía."
    assert all(isinstance(item, str) for item in billers_list), "La lista de facturadores debe contener strings."
