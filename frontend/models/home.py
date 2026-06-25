from dataclasses import dataclass, field


# ── Admin Models ────────────────────────────────

@dataclass
class HomeAdminKpis:
    total_records: int = 0
    records_today: int = 0
    active_users: int = 0
    total_valor_tercero: float = 0.0
    compliance: float = 0.0
    horas_productivas_equipo: float = 0.0
    cumplimiento_horas: float = 0.0


@dataclass
class HomeAdminModuleCount:
    legalizaciones: int = 0
    facturacion: int = 0
    rips: int = 0
    radicacion: int = 0
    procesos: int = 0


@dataclass
class HomeAdminTrendPoint:
    fecha: str = ""
    legalizaciones: int = 0
    facturacion: int = 0
    rips: int = 0
    radicacion: int = 0
    procesos: int = 0


@dataclass
class HomeAdminTopUser:
    usuario: str = ""
    registros: int = 0
    horas_productivas: float = 0.0


@dataclass
class HomeAdminModuleCompliance:
    modulo: str = ""
    porcentaje: float = 0.0


@dataclass
class HomeAdminAlert:
    icon: str = ""
    text: str = ""
    severity: str = "warning"


@dataclass
class HomeAdminInsight:
    text: str = ""


@dataclass
class HomeAdminResponse:
    kpis: HomeAdminKpis = field(default_factory=HomeAdminKpis)
    modules: HomeAdminModuleCount = field(default_factory=HomeAdminModuleCount)
    trend: list[HomeAdminTrendPoint] = field(default_factory=list)
    top_users: list[HomeAdminTopUser] = field(default_factory=list)
    module_compliance: list[HomeAdminModuleCompliance] = field(default_factory=list)
    alerts: list[HomeAdminAlert] = field(default_factory=list)
    insights: list[HomeAdminInsight] = field(default_factory=list)


# ── User Models ─────────────────────────────────

@dataclass
class HomeUserKpis:
    registros_hoy: int = 0
    radicaciones_pendientes: int = 0
    horas_productivas: float = 0.0
    horas_esperadas: float = 0.0
    cumplimiento_horas: float = 0.0


@dataclass
class HomeUserModuleCount:
    legalizaciones: int = 0
    facturacion: int = 0
    rips: int = 0
    radicacion: int = 0
    procesos: int = 0
    valor_facturado: float = 0.0


@dataclass
class HomeUserTrendPoint:
    fecha: str = ""
    registros: int = 0


@dataclass
class HomeUserPendiente:
    icon: str = ""
    text: str = ""
    count: int = 0


@dataclass
class HomeUserAlert:
    icon: str = ""
    text: str = ""


@dataclass
class HomeUserInsight:
    text: str = ""


@dataclass
class HomeUserResponse:
    kpis: HomeUserKpis = field(default_factory=HomeUserKpis)
    modules: HomeUserModuleCount = field(default_factory=HomeUserModuleCount)
    trend: list[HomeUserTrendPoint] = field(default_factory=list)
    pendientes: list[HomeUserPendiente] = field(default_factory=list)
    alerts: list[HomeUserAlert] = field(default_factory=list)
    insights: list[HomeUserInsight] = field(default_factory=list)
