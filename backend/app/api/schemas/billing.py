from datetime import date, datetime
from pydantic import BaseModel, Field


class BillingPeriod(BaseModel):
    start_date: str
    end_date: str
    last_update: str


class BillingKpis(BaseModel):
    total_records: int = 0
    total_valor_tercero: float = 0.0
    active_users: int = 0
    active_eps: int = 0
    active_convenios: int = 0
    average_ticket: float = 0.0
    daily_avg_records: float = 0.0
    daily_avg_valor_tercero: float = 0.0
    tiempo_total_horas: float = 0.0
    tiempo_promedio_diario_horas: float = 0.0


class BillingSummaryResponse(BaseModel):
    period: BillingPeriod
    kpis: BillingKpis


class BillingUserDistributionItem(BaseModel):
    usuario: str
    records: int
    valor: float
    ticket_promedio: float
    participacion_records: float
    participacion_valor: float


class BillingDailyTrendItem(BaseModel):
    date: str
    records: int
    valor: float
    ticket_promedio: float


class BillingEpsDistributionItem(BaseModel):
    eps: str
    records: int
    valor: float


class BillingConvenioDistributionItem(BaseModel):
    convenio: str
    records: int
    valor: float


class BillingTopRecordsItem(BaseModel):
    usuario: str
    records: int


class BillingTopValorItem(BaseModel):
    usuario: str
    valor: float


class BillingRankings(BaseModel):
    top_records: list[BillingTopRecordsItem] = Field(default_factory=list)
    top_valor: list[BillingTopValorItem] = Field(default_factory=list)


class BillingInsightItem(BaseModel):
    type: str
    title: str
    description: str


class BillingAnalyticsResponse(BaseModel):
    user_distribution: list[BillingUserDistributionItem] = Field(default_factory=list)
    daily_trend: list[BillingDailyTrendItem] = Field(default_factory=list)
    eps_distribution: list[BillingEpsDistributionItem] = Field(default_factory=list)
    convenio_distribution: list[BillingConvenioDistributionItem] = Field(default_factory=list)
    rankings: BillingRankings = Field(default_factory=BillingRankings)
    insights: list[BillingInsightItem] = Field(default_factory=list)


class BillingPagination(BaseModel):
    page: int = 1
    page_size: int = 50
    total: int = 0


class BillingFilterOptions(BaseModel):
    users: list[str] = Field(default_factory=list)
    eps: list[str] = Field(default_factory=list)
    convenios: list[str] = Field(default_factory=list)
    estado: list[str] = Field(default_factory=list)


class BillingDetailItem(BaseModel):
    identificacion: str | None = None
    prefijo: str | None = None
    factura: str | None = None
    fecha_factura: str | None = None
    fecha_legalizacion: str | None = None
    paciente: str | None = None
    valor_paciente: float | None = None
    valor_tercero: float | None = None
    eps: str | None = None
    convenio: str | None = None
    usuario: str | None = None
    estado: str | None = None


class BillingDetailResponse(BaseModel):
    pagination: BillingPagination
    filters: BillingFilterOptions = Field(default_factory=BillingFilterOptions)
    data: list[BillingDetailItem] = Field(default_factory=list)
