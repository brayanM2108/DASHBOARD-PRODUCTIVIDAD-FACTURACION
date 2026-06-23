from typing import Any

import requests
from frontend.api.api_client import build_api_url
from frontend.exceptions import ApiException, UnauthorizedException


class HomeApi:

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
        response.raise_for_status()
        return response.json()

    def get_admin_summary(
        self,
        start_date,
        end_date,
        filter_user: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
        if filter_user:
            params["filter_user"] = filter_user
        return self._get("home/admin/summary", params)

    def get_user_summary(
        self,
        start_date,
        end_date,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
        return self._get("home/user/summary", params)
