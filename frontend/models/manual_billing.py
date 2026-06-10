from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProcessRecord:
    id: int
    fecha: str
    nombre: str
    documento: str
    proceso: str
    cantidad: int
    usuario_id: int
    created_at: str
    observacion: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class ProcessSummary:
    total_records: int = 0
    total_quantity: int = 0
    unique_people: int = 0
    unique_processes: int = 0
