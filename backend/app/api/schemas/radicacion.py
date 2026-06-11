from pydantic import BaseModel, Field


class RadicacionByUserRecord(BaseModel):
    USUARIO: str | None = None
    TOTAL: int | None = None
    VENCIDAS: int | None = None


class RadicacionMetricsResponse(BaseModel):
    total: int = 0
    vencidas: int = 0
    porcentaje_vencidas: float = 0.0
    by_user: list[RadicacionByUserRecord] = Field(default_factory=list)
