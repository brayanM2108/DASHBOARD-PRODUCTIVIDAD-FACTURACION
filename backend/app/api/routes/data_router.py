import os
import json
import pandas as pd

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from ..deps.auth_deps import get_current_user, require_roles
from ...etl.file_helpers import read_file_robust
from ...etl.loaders import (
    load_all_persisted_frames,
    load_billers_master_cached,
    DATASET_TO_FILE_KEY,
)
from ...etl.loaders.parquet_loader import save_all_persisted_frames
from ...etl.loaders.billers_loader import normalize_billers_document_column, save_billers_to_file
from ...etl.transformers.electronic_billing_transformer import process_electronic_billing_data
from ...etl.utils.dataframe_helpers import normalize_columns_upper_in_place
from ...services.legalizations_service import process_legalizations
from ...services.rips_service import process_rips
from ...utils.config.settings import FILES

router = APIRouter(prefix="/data", tags=["data"])

_MARKERS = {
    "legalizations_df": "ID_LEGALIZACION",
    "electronic_billing_df": "IDENTIFICACION",
    "rips_df": "ESTADO_COMPLETITUD",
}

_PROCESSORS = {
    "legalizations_df": process_legalizations,
    "electronic_billing_df": process_electronic_billing_data,
    "rips_df": process_rips,
}

_PROCESSORS_NEED_BILLERS = {"legalizations_df", "rips_df"}


@router.post("/upload")
async def upload_data(
    file: UploadFile = File(...),
    module_key: str = Form(...),
    current_user=Depends(require_roles("ADMIN", "SUPERVISOR")),
):
    if module_key not in _PROCESSORS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Módulo desconocido: {module_key}",
        )

    marker = _MARKERS.get(module_key)
    if marker is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No hay marcador definido para: {module_key}",
        )

    df_raw, header_row = read_file_robust(file.file, marker)
    if df_raw is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No se encontró la columna marcadora esperada en el archivo.",
        )

    processor = _PROCESSORS[module_key]
    try:
        if module_key in _PROCESSORS_NEED_BILLERS:
            billers_df = load_billers_master_cached()
            result = processor(df_raw, billers_df)
        else:
            result = processor(df_raw)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error al procesar: {str(e)}",
        )

    if isinstance(result, dict):
        if result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=result["error"],
            )
        df_processed = result.get(module_key)
    else:
        df_processed = result

    if df_processed is None or (hasattr(df_processed, "empty") and df_processed.empty):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El archivo no contiene datos válidos después del procesamiento.",
        )

    save_all_persisted_frames({module_key: df_processed})

    return {
        "status": "ok",
        "module": module_key,
        "records": len(df_processed),
    }


@router.post("/upload/billers")
async def upload_billers(
    file: UploadFile = File(...),
    current_user=Depends(require_roles("ADMIN", "SUPERVISOR")),
):
    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file.file)
        else:
            df = pd.read_excel(file.file)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error al leer el archivo: {str(e)}",
        )

    df = normalize_columns_upper_in_place(df)
    df = normalize_billers_document_column(df)

    save_billers_to_file(df)
    save_all_persisted_frames({"billers_df": df})

    return {
        "status": "ok",
        "module": "billers_df",
        "records": len(df),
    }


@router.get("/load")
def load_data(
    include_data: bool = False,
    current_user=Depends(get_current_user),
):
    import logging
    logger = logging.getLogger(__name__)

    datasets = load_all_persisted_frames()

    billers_df = datasets.get("billers_df")
    if billers_df is None or (hasattr(billers_df, "empty") and billers_df.empty):
        billers_df = load_billers_master_cached()
        if billers_df is not None and not billers_df.empty:
            datasets["billers_df"] = billers_df
            save_all_persisted_frames({"billers_df": billers_df})

    result = {}
    for key, df in datasets.items():
        if df is not None and not df.empty:
            entry = {
                "records": len(df),
                "columns": list(df.columns),
            }
            if include_data:
                try:
                    entry["data"] = json.loads(df.to_json(orient="records", date_format="iso"))
                except Exception as e:
                    logger.error("Failed to serialize dataset %s: %s", key, e)
                    entry["data"] = None
            result[key] = entry
        else:
            result[key] = None

    logger.info("Data load: %s datasets, include_data=%s",
                {k: (v["records"] if v else 0) for k, v in result.items()},
                include_data)
    return result


@router.get("/load/{dataset_key}")
def load_dataset(
    dataset_key: str,
    current_user=Depends(get_current_user),
):
    datasets = load_all_persisted_frames()
    df = datasets.get(dataset_key)

    if dataset_key == "billers_df" and (df is None or df.empty):
        df = load_billers_master_cached()

    if df is None or df.empty:
        return {"dataset": dataset_key, "data": None, "records": 0}
    return {
        "dataset": dataset_key,
        "records": len(df),
        "data": json.loads(df.astype(str).to_json(orient="records")),
    }


@router.delete("/{file_key}")
def delete_data(
    file_key: str,
    current_user=Depends(require_roles("ADMIN", "SUPERVISOR")),
):
    allowed_keys = {"Legalizaciones", "Facturacion", "FacturacionElectronica", "ArchivoProcesos", "Rips", "Facturadores"}
    if file_key not in allowed_keys:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Clave de archivo no válida: {file_key}",
        )

    if file_key in FILES and os.path.exists(FILES[file_key]):
        try:
            os.remove(FILES[file_key])
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar {file_key}: {str(e)}",
            )

    return {"status": "ok", "deleted": file_key}
