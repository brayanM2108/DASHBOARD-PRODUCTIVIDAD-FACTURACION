from pydantic import BaseModel


class LegalizationByUserRecord(BaseModel):
    USUARIO: str | None = None
    REGISTROS: int | None = None


class LegalizationByDateRecord(BaseModel):
    DATE: str | None = None
    REGISTROS: int | None = None
    VALOR_TERCERO: float | None = None


class LegalizationMetricsResponse(BaseModel):
    total_records: int = 0
    daily_avg_records: float = 0.0

    by_user: list[LegalizationByUserRecord] = []
    by_date: list[LegalizationByDateRecord] = []

    error: str | None = None