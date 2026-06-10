from dataclasses import dataclass, field


@dataclass
class BillingByUserRecord:
    USUARIO: str | None = None
    REGISTROS: int | None = None
    VALOR_TERCERO: float | None = None


@dataclass
class BillingByDateRecord:
    DATE: str | None = None
    REGISTROS: int | None = None
    VALOR_TERCERO: float | None = None


@dataclass
class BillingMetrics:
    total_records: int = 0
    total_valor_tercero: float = 0.0
    daily_avg_records: float = 0.0
    daily_avg_valor_tercero: float = 0.0
    by_user: list[BillingByUserRecord] = field(default_factory=list)
    by_date: list[BillingByDateRecord] = field(default_factory=list)
