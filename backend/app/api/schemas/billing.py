from pydantic import BaseModel


class BillingByUserRecord(BaseModel):
    USUARIO: str | None = None
    REGISTROS: int | None = None
    VALOR_TERCERO: float | None = None


class BillingByDateRecord(BaseModel):
    DATE: str | None = None
    REGISTROS: int | None = None
    VALOR_TERCERO: float | None = None


class BillingMetricsResponse(BaseModel):
    total_records: int = 0
    total_valor_tercero: float = 0.0
    daily_avg_records: float = 0.0
    daily_avg_valor_tercero: float = 0.0
    by_user: list[dict] = []
    by_date: list[dict] = []
    error: str | None = None
