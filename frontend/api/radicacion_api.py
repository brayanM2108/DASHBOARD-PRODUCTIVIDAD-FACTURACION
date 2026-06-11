from typing import Any

import requests

from frontend.api.api_client import build_api_url


class RadicacionApi:

    def __init__(self, token: str | None = None):
        self.token = token

    def _headers(self) -> dict:
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    def get_metrics(
        self,
        start_date=None,
        end_date=None,
        selected_users: list[str] | None = None,
    ) -> dict[str, Any]:
        url = build_api_url("radicacion/metrics")
        params: dict[str, Any] = {}
        if start_date:
            params["start_date"] = str(start_date)
        if end_date:
            params["end_date"] = str(end_date)
        if selected_users:
            params["selected_users"] = selected_users
        try:
            response = requests.get(url, params=params, headers=self._headers(), timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Error al obtener métricas de radicación: {e}")
