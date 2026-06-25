from fastapi import APIRouter, Depends

from ...services.process_config_service import ProcessConfigService
from ..deps import require_roles
from ..schemas.process_config import ProcessConfigResponse, ProcessConfigUpdate

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


@router.get("/process-config", response_model=ProcessConfigResponse)
def get_process_config(
    current_user=Depends(require_roles("ADMIN")),
):
    data = ProcessConfigService.read_config()
    return ProcessConfigResponse(**data)


@router.put("/process-config", response_model=ProcessConfigResponse)
def update_process_config(
    body: ProcessConfigUpdate,
    current_user=Depends(require_roles("ADMIN")),
):
    ProcessConfigService.write_config(body.model_dump())
    return ProcessConfigResponse(**body.model_dump())
