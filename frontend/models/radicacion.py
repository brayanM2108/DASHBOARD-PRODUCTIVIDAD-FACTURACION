from dataclasses import dataclass, field


@dataclass
class RadicacionByUserRecord:
    USUARIO: str | None = None
    TOTAL: int | None = None
    VENCIDAS: int | None = None


@dataclass
class RadicacionMetrics:
    total: int = 0
    vencidas: int = 0
    porcentaje_vencidas: float = 0.0
    by_user: list[RadicacionByUserRecord] = field(default_factory=list)
    error: str | None = None
