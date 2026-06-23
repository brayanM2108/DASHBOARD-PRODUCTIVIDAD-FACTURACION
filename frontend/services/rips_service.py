from datetime import date

import pandas as pd

from frontend.api.rips_api import RipsApi
from frontend.models.rips import RipsMetrics, RipsProductivityMetrics


class RipsFrontendService:

    def __init__(self):
        self.api = RipsApi()

    def get_metrics(self, start_date: date, end_date: date, selected_users: list[str] | None = None) -> RipsMetrics:
        try:
            response = self.api.get_metrics(
                start_date=start_date,
                end_date=end_date,
                selected_users=selected_users,
            )
            return RipsMetrics(
                metrics=RipsProductivityMetrics(
                    total=response.get("total", 0),
                    daily_average=response.get("daily_average", 0.0),
                    by_user=response.get("by_user") or [],
                    by_date=response.get("by_date") or [],
                    category=response.get("category"),
                    tiempo_total_horas=response.get("tiempo_total_horas", 0.0),
                    tiempo_promedio_diario_horas=response.get("tiempo_promedio_diario_horas", 0.0),
                ),
            )
        except Exception as e:
            return RipsMetrics(
                metrics=RipsProductivityMetrics(),
                error=str(e),
            )

    def to_dataframe(self, records: list) -> pd.DataFrame:
        if not records:
            return pd.DataFrame()
        return pd.DataFrame(records)
