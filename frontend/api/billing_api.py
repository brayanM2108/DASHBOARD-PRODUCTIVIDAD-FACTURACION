from typing import Any

import requests
from frontend.api.api_client import build_api_url
from frontend.exceptions import ApiException, UnauthorizedException, NotFoundException


class ElectronicBillingApi:

    def __init__(self, token: str | None = None):
        self.token = token

    def _headers(self) -> dict:
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        url = build_api_url(path)
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

    def get_summary(
        self,
        start_date,
        end_date,
        selected_users: list[str] | None = None,
        selected_agreement: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "start_date": start_date,
            "end_date": end_date,
        }
        if selected_users:
            params["selected_users"] = selected_users
        if selected_agreement:
            params["selected_agreement"] = selected_agreement
        return self._get("billing/summary", params)

    def get_analytics(
        self,
        start_date,
        end_date,
        selected_users: list[str] | None = None,
        selected_agreement: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "start_date": start_date,
            "end_date": end_date,
        }
        if selected_users:
            params["selected_users"] = selected_users
        if selected_agreement:
            params["selected_agreement"] = selected_agreement
        return self._get("billing/analytics", params)

    def get_detail(
        self,
        start_date,
        end_date,
        selected_users: list[str] | None = None,
        selected_agreement: str | None = None,
        page: int = 1,
        page_size: int = 50,
        filter_user: str | None = None,
        filter_eps: str | None = None,
        filter_convenio: str | None = None,
        filter_estado: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "start_date": start_date,
            "end_date": end_date,
            "page": page,
            "page_size": page_size,
        }
        if selected_users:
            params["selected_users"] = selected_users
        if selected_agreement:
            params["selected_agreement"] = selected_agreement
        if filter_user:
            params["filter_user"] = filter_user
        if filter_eps:
            params["filter_eps"] = filter_eps
        if filter_convenio:
            params["filter_convenio"] = filter_convenio
        if filter_estado:
            params["filter_estado"] = filter_estado
        return self._get("billing/detail", params)
