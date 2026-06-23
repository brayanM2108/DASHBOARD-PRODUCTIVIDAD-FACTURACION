from pydantic import BaseModel, Field


class LegalizationByUserRecord(BaseModel):
    USUARIO: str | None = None
    REGISTROS: int | None = None
    TIEMPO_HORAS: float | None = None


class LegalizationByDateRecord(BaseModel):
    DATE: str | None = None
    REGISTROS: int | None = None
    TIEMPO_HORAS: float | None = None

class ProductivityMetricsResponse(BaseModel):

    total: int = 0

    daily_average: float = 0.0

    by_user: list[LegalizationByUserRecord] = Field(
        default_factory=list
    )

    by_date: list[LegalizationByDateRecord] = Field(
        default_factory=list
    )

    category: str | None = None

    tiempo_total_horas: float = 0.0

    tiempo_promedio_diario_horas: float = 0.0


class LegalizationMetricsResponse(BaseModel):

    ppl: ProductivityMetricsResponse

    agreements: ProductivityMetricsResponse