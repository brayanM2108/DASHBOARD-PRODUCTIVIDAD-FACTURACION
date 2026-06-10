from dataclasses import dataclass, field


@dataclass
class RipsProductivityMetrics:
    total: int = 0
    daily_average: float = 0.0
    by_user: list[dict] = field(default_factory=list)
    by_date: list[dict] = field(default_factory=list)
    category: str | None = None


@dataclass
class RipsMetrics:
    metrics: RipsProductivityMetrics
    error: str | None = None
