from typing import Any

import requests
from api.auth_api import build_api_url
from frontend.exceptions import ApiException, UnauthorizedException, NotFoundException


class ElectronicBillingApi:

    def __init__(self, token: str | None = None):
        self.token = token

    def _headers(self) -> dict:
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    def get_metrics(
        self,
        start_date,
        end_date,
        selected_users: list[str] | None = None,
        selected_agreement: str | None = None,
    ) -> dict[str, Any]:
        url = build_api_url("billing/metrics")
        params: dict[str, Any] = {
            "start_date": start_date,
            "end_date": end_date,
        }
        if selected_users:
            params["selected_users"] = selected_users
        if selected_agreement:
            params["selected_agreement"] = selected_agreement

        try:
            response = requests.get(url, params=params, headers=self._headers(), timeout=60)
        except requests.RequestException as e:
            raise ApiException(f"Connection error: {e}")

        if response.status_code == 401:
            raise UnauthorizedException()
        if response.status_code == 404:
            raise NotFoundException()

        response.raise_for_status()
        return response.json()
