from datetime import date

from frontend.api.billing_api import ElectronicBillingApi
from frontend.models.billing import (
    BillingAnalytics,
    BillingConvenioDistributionItem,
    BillingDailyTrendItem,
    BillingDetail,
    BillingDetailItem,
    BillingEpsDistributionItem,
    BillingInsightItem,
    BillingKpis,
    BillingPeriod,
    BillingPagination,
    BillingRankings,
    BillingFilterOptions,
    BillingSummary,
    BillingTopRecordsItem,
    BillingTopValorItem,
    BillingUserDistributionItem,
)


class ElectronicBillingFrontendService:

    def __init__(self, token: str | None = None):
        self.api = ElectronicBillingApi(token=token)

    def get_summary(
        self,
        start_date: date,
        end_date: date,
        selected_users: list[str] | None = None,
        selected_agreement: str | None = None,
    ) -> BillingSummary:
        response = self.api.get_summary(
            start_date=start_date,
            end_date=end_date,
            selected_users=selected_users,
            selected_agreement=selected_agreement,
        )
        period_raw = response.get("period", {})
        kpis_raw = response.get("kpis", {})
        return BillingSummary(
            period=BillingPeriod(**period_raw) if period_raw else None,
            kpis=BillingKpis(**kpis_raw) if kpis_raw else None,
        )

    def get_analytics(
        self,
        start_date: date,
        end_date: date,
        selected_users: list[str] | None = None,
        selected_agreement: str | None = None,
    ) -> BillingAnalytics:
        response = self.api.get_analytics(
            start_date=start_date,
            end_date=end_date,
            selected_users=selected_users,
            selected_agreement=selected_agreement,
        )
        return BillingAnalytics(
            user_distribution=[
                BillingUserDistributionItem(**u) for u in response.get("user_distribution", [])
            ],
            daily_trend=[
                BillingDailyTrendItem(**d) for d in response.get("daily_trend", [])
            ],
            eps_distribution=[
                BillingEpsDistributionItem(**e) for e in response.get("eps_distribution", [])
            ],
            convenio_distribution=[
                BillingConvenioDistributionItem(**c) for c in response.get("convenio_distribution", [])
            ],
            rankings=BillingRankings(
                top_records=[
                    BillingTopRecordsItem(**r) for r in response.get("rankings", {}).get("top_records", [])
                ],
                top_valor=[
                    BillingTopValorItem(**v) for v in response.get("rankings", {}).get("top_valor", [])
                ],
            ),
            insights=[
                BillingInsightItem(**i) for i in response.get("insights", [])
            ],
        )

    def get_detail(
        self,
        start_date: date,
        end_date: date,
        selected_users: list[str] | None = None,
        selected_agreement: str | None = None,
        page: int = 1,
        page_size: int = 50,
        filter_user: str | None = None,
        filter_eps: str | None = None,
        filter_convenio: str | None = None,
        filter_estado: str | None = None,
    ) -> BillingDetail:
        response = self.api.get_detail(
            start_date=start_date,
            end_date=end_date,
            selected_users=selected_users,
            selected_agreement=selected_agreement,
            page=page,
            page_size=page_size,
            filter_user=filter_user,
            filter_eps=filter_eps,
            filter_convenio=filter_convenio,
            filter_estado=filter_estado,
        )
        pagination_raw = response.get("pagination", {})
        filters_raw = response.get("filters", {})
        return BillingDetail(
            pagination=BillingPagination(**pagination_raw),
            filters=BillingFilterOptions(
                users=filters_raw.get("users", []),
                eps=filters_raw.get("eps", []),
                convenios=filters_raw.get("convenios", []),
                estado=filters_raw.get("estado", []),
            ),
            data=[BillingDetailItem(**item) for item in response.get("data", [])],
        )
