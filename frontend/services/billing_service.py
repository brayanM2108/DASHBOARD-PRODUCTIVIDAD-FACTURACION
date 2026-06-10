from datetime import date

from frontend.api.billing_api import ElectronicBillingApi
from frontend.models.billing import BillingMetrics, BillingByUserRecord, BillingByDateRecord


class ElectronicBillingFrontendService:

    def __init__(self, token: str | None = None):
        self.api = ElectronicBillingApi(token=token)

    def get_metrics(
        self,
        start_date: date,
        end_date: date,
        selected_users: list[str] | None = None,
        selected_agreement: str | None = None,
    ) -> BillingMetrics:
        response = self.api.get_metrics(
            start_date=start_date,
            end_date=end_date,
            selected_users=selected_users,
            selected_agreement=selected_agreement,
        )

        by_user = [
            BillingByUserRecord(**record)
            for record in response.get("by_user", [])
        ]
        by_date = [
            BillingByDateRecord(**record)
            for record in response.get("by_date", [])
        ]

        return BillingMetrics(
            total_records=response.get("total_records", 0),
            total_valor_tercero=response.get("total_valor_tercero", 0.0),
            daily_avg_records=response.get("daily_avg_records", 0.0),
            daily_avg_valor_tercero=response.get("daily_avg_valor_tercero", 0.0),
            by_user=by_user,
            by_date=by_date,
        )
