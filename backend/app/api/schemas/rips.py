from pydantic import BaseModel, Field


class RipsByUserRecord(BaseModel):
    USUARIO_QUE_COMPLETA_RIPS: str | None = None
    REGISTROS: int | None = None
    TIEMPO_HORAS: float | None = None


class RipsByDateRecord(BaseModel):
    DATE: str | None = None
    REGISTROS: int | None = None
    TIEMPO_HORAS: float | None = None


class RipsMetricsResponse(BaseModel):
    total: int = 0
    daily_average: float = 0.0
    by_user: list[RipsByUserRecord] = Field(default_factory=list)
    by_date: list[RipsByDateRecord] = Field(default_factory=list)
    category: str | None = None
    tiempo_total_horas: float = 0.0
    tiempo_promedio_diario_horas: float = 0.0
