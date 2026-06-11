from datetime import date

from frontend.api.radicacion_api import RadicacionApi
from frontend.models.radicacion import RadicacionMetrics, RadicacionByUserRecord


class RadicacionFrontendService:

    def __init__(self, token: str | None = None):
        self.api = RadicacionApi(token=token)

    def get_metrics(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        selected_users: list[str] | None = None,
    ) -> RadicacionMetrics:
        try:
            response = self.api.get_metrics(
                start_date=start_date,
                end_date=end_date,
                selected_users=selected_users,
            )
            by_user = [RadicacionByUserRecord(**r) for r in response.get("by_user", [])]
            return RadicacionMetrics(
                total=response.get("total", 0),
                vencidas=response.get("vencidas", 0),
                porcentaje_vencidas=response.get("porcentaje_vencidas", 0.0),
                by_user=by_user,
            )
        except Exception as e:
            return RadicacionMetrics(error=str(e))
