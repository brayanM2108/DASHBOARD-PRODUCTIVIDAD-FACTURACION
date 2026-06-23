from dataclasses import dataclass, field


@dataclass
class BillingPeriod:
    start_date: str
    end_date: str
    last_update: str


@dataclass
class BillingKpis:
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


@dataclass
class BillingSummary:
    period: BillingPeriod | None = None
    kpis: BillingKpis | None = None


@dataclass
class BillingUserDistributionItem:
    usuario: str = ""
    records: int = 0
    valor: float = 0.0
    ticket_promedio: float = 0.0
    participacion_records: float = 0.0
    participacion_valor: float = 0.0


@dataclass
class BillingDailyTrendItem:
    date: str = ""
    records: int = 0
    valor: float = 0.0
    ticket_promedio: float = 0.0


@dataclass
class BillingEpsDistributionItem:
    eps: str = ""
    records: int = 0
    valor: float = 0.0


@dataclass
class BillingConvenioDistributionItem:
    convenio: str = ""
    records: int = 0
    valor: float = 0.0


@dataclass
class BillingTopRecordsItem:
    usuario: str = ""
    records: int = 0


@dataclass
class BillingTopValorItem:
    usuario: str = ""
    valor: float = 0.0


@dataclass
class BillingRankings:
    top_records: list[BillingTopRecordsItem] = field(default_factory=list)
    top_valor: list[BillingTopValorItem] = field(default_factory=list)


@dataclass
class BillingInsightItem:
    type: str = ""
    title: str = ""
    description: str = ""


@dataclass
class BillingAnalytics:
    user_distribution: list[BillingUserDistributionItem] = field(default_factory=list)
    daily_trend: list[BillingDailyTrendItem] = field(default_factory=list)
    eps_distribution: list[BillingEpsDistributionItem] = field(default_factory=list)
    convenio_distribution: list[BillingConvenioDistributionItem] = field(default_factory=list)
    rankings: BillingRankings = field(default_factory=BillingRankings)
    insights: list[BillingInsightItem] = field(default_factory=list)


@dataclass
class BillingPagination:
    page: int = 1
    page_size: int = 50
    total: int = 0


@dataclass
class BillingFilterOptions:
    users: list[str] = field(default_factory=list)
    eps: list[str] = field(default_factory=list)
    convenios: list[str] = field(default_factory=list)
    estado: list[str] = field(default_factory=list)


@dataclass
class BillingDetailItem:
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


@dataclass
class BillingDetail:
    pagination: BillingPagination = field(default_factory=BillingPagination)
    filters: BillingFilterOptions = field(default_factory=BillingFilterOptions)
    data: list[BillingDetailItem] = field(default_factory=list)
