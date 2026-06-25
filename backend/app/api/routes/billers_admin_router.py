from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..deps.auth_deps import require_roles
from ...etl.loaders import load_billers_from_file, save_billers_to_file
from ...etl.loaders.parquet_loader import save_all_persisted_frames


class BillerEntry(BaseModel):
    NOMBRE: str
    DOCUMENTO: str
    ROL: str


class BillersUpdateRequest(BaseModel):
    facturadores: list[BillerEntry]


router = APIRouter(prefix="/admin/billers", tags=["admin", "billers"])


@router.get("")
def list_billers(current_user=Depends(require_roles("ADMIN"))):
    df = load_billers_from_file()
    if df is None:
        return {"facturadores": []}
    return {"facturadores": df.fillna("").to_dict(orient="records")}


@router.put("")
def update_billers(
    payload: BillersUpdateRequest,
    current_user=Depends(require_roles("ADMIN")),
):
    import pandas as pd
    df = pd.DataFrame([b.model_dump() for b in payload.facturadores])
    if not save_billers_to_file(df):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al guardar facturadores",
        )
    save_all_persisted_frames({"billers_df": df})
    return {"status": "ok", "count": len(df)}
