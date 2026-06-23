from datetime import date

from frontend.api.legalizations_api import LegalizationsApi
from frontend.models.legalizations import (
    LegalizationMetrics,
    ProductivityMetrics,
)


class LegalizationsService:

    def __init__(self):
        self.api = LegalizationsApi()

    def get_metrics(
            self,
            start_date: date,
            end_date: date,
            selected_users: list[str] | None = None,
    ) -> LegalizationMetrics:

        response = self.api.get_metrics(
            start_date=start_date,
            end_date=end_date,
            selected_users=selected_users,
        )

        ppl = response.get("ppl", {})
        agreements = response.get("agreements", {})

        return LegalizationMetrics(
            ppl=ProductivityMetrics(
                total=ppl.get("total", 0),
                daily_average=ppl.get("daily_average", 0.0),
                by_user=ppl.get("by_user") or [],
                by_date=ppl.get("by_date") or [],
                category=ppl.get("category"),
                tiempo_total_horas=ppl.get("tiempo_total_horas", 0.0),
                tiempo_promedio_diario_horas=ppl.get("tiempo_promedio_diario_horas", 0.0),
            ),
            agreements=ProductivityMetrics(
                total=agreements.get("total", 0),
                daily_average=agreements.get("daily_average", 0.0),
                by_user=agreements.get("by_user") or [],
                by_date=agreements.get("by_date") or [],
                category=agreements.get("category"),
                tiempo_total_horas=agreements.get("tiempo_total_horas", 0.0),
                tiempo_promedio_diario_horas=agreements.get("tiempo_promedio_diario_horas", 0.0),
            ),
        )