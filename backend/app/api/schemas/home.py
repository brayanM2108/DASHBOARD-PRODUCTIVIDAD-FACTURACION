from pydantic import BaseModel, Field


# ── Admin Schemas ───────────────────────────────

class HomeAdminKpis(BaseModel):
    total_records: int = 0
    records_today: int = 0
    active_users: int = 0
    total_valor_tercero: float = 0.0
    compliance: float = 0.0


class HomeAdminModuleCount(BaseModel):
    legalizaciones: int = 0
    facturacion: int = 0
    rips: int = 0
    radicacion: int = 0
    procesos: int = 0


class HomeAdminTrendPoint(BaseModel):
    fecha: str
    legalizaciones: int = 0
    facturacion: int = 0
    rips: int = 0
    radicacion: int = 0
    procesos: int = 0


class HomeAdminTopUser(BaseModel):
    usuario: str
    registros: int


class HomeAdminModuleCompliance(BaseModel):
    modulo: str
    porcentaje: float


class HomeAdminAlert(BaseModel):
    icon: str = ""
    text: str = ""
    severity: str = "warning"


class HomeAdminInsight(BaseModel):
    text: str = ""


class HomeAdminResponse(BaseModel):
    kpis: HomeAdminKpis = Field(default_factory=HomeAdminKpis)
    modules: HomeAdminModuleCount = Field(default_factory=HomeAdminModuleCount)
    trend: list[HomeAdminTrendPoint] = Field(default_factory=list)
    top_users: list[HomeAdminTopUser] = Field(default_factory=list)
    module_compliance: list[HomeAdminModuleCompliance] = Field(default_factory=list)
    alerts: list[HomeAdminAlert] = Field(default_factory=list)
    insights: list[HomeAdminInsight] = Field(default_factory=list)


# ── User Schemas ────────────────────────────────

class HomeUserKpis(BaseModel):
    registros_hoy: int = 0
    radicaciones_pendientes: int = 0
    horas_productivas: float = 0.0


class HomeUserModuleCount(BaseModel):
    legalizaciones: int = 0
    facturacion: int = 0
    rips: int = 0
    radicacion: int = 0
    procesos: int = 0
    valor_facturado: float = 0.0


class HomeUserTrendPoint(BaseModel):
    fecha: str
    registros: int = 0


class HomeUserPendiente(BaseModel):
    icon: str = ""
    text: str = ""
    count: int = 0


class HomeUserAlert(BaseModel):
    icon: str = ""
    text: str = ""


class HomeUserInsight(BaseModel):
    text: str = ""


class HomeUserResponse(BaseModel):
    kpis: HomeUserKpis = Field(default_factory=HomeUserKpis)
    modules: HomeUserModuleCount = Field(default_factory=HomeUserModuleCount)
    trend: list[HomeUserTrendPoint] = Field(default_factory=list)
    pendientes: list[HomeUserPendiente] = Field(default_factory=list)
    alerts: list[HomeUserAlert] = Field(default_factory=list)
    insights: list[HomeUserInsight] = Field(default_factory=list)
