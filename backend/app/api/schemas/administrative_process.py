from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class ProcessCreate(BaseModel):
    fecha: date
    proceso: str = Field(..., min_length=1, max_length=255)
    cantidad: int = Field(..., ge=1)
    observacion: Optional[str] = None


class ProcessUpdate(BaseModel):
    fecha: Optional[date] = None
    proceso: Optional[str] = None
    cantidad: Optional[int] = None
    observacion: Optional[str] = None


class ProcessOut(BaseModel):
    id: int
    fecha: date
    nombre: str
    documento: str
    proceso: str
    cantidad: int
    observacion: Optional[str] = None
    usuario_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ProcessFilter(BaseModel):
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    proceso: Optional[str] = None


class ProcessSummary(BaseModel):
    total_records: int
    total_quantity: int
    unique_people: int
    unique_processes: int
