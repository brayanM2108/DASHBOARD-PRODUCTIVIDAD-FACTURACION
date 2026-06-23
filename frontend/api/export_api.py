from datetime import date
from typing import Any

import requests
from frontend.api.api_client import build_api_url
from frontend.exceptions import ApiException, UnauthorizedException


class ExportApi:

    def __init__(self, token: str | None = None):
        self.token = token

    def _headers(self) -> dict:
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    def _get_bytes(self, path: str, params: dict[str, Any]) -> bytes:
        url = build_api_url(path)
        try:
            response = requests.get(url, params=params, headers=self._headers(), timeout=120)
        except requests.RequestException as e:
            raise ApiException(f"Connection error: {e}")

        if response.status_code == 401:
            raise UnauthorizedException()
        response.raise_for_status()
        return response.content

    def _base_params(self, start_date: date, end_date: date, selected_users: list[str] | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
        if selected_users:
            params["selected_users"] = selected_users
        return params

    def get_general_export(
        self,
        start_date: date,
        end_date: date,
        selected_users: list[str] | None = None,
    ) -> bytes:
        return self._get_bytes("export/general", self._base_params(start_date, end_date, selected_users))

    def get_billing_export(
        self,
        start_date: date,
        end_date: date,
        selected_users: list[str] | None = None,
    ) -> bytes:
        return self._get_bytes("export/billing", self._base_params(start_date, end_date, selected_users))

    def get_legalizations_export(
        self,
        start_date: date,
        end_date: date,
        selected_users: list[str] | None = None,
    ) -> bytes:
        return self._get_bytes("export/legalizations", self._base_params(start_date, end_date, selected_users))

    def get_rips_export(
        self,
        start_date: date,
        end_date: date,
        selected_users: list[str] | None = None,
    ) -> bytes:
        return self._get_bytes("export/rips", self._base_params(start_date, end_date, selected_users))

    def get_radicacion_export(
        self,
        start_date: date,
        end_date: date,
        selected_users: list[str] | None = None,
    ) -> bytes:
        return self._get_bytes("export/radicacion", self._base_params(start_date, end_date, selected_users))

    def get_processes_export(
        self,
        start_date: date,
        end_date: date,
        selected_users: list[str] | None = None,
    ) -> bytes:
        return self._get_bytes("export/processes", self._base_params(start_date, end_date, selected_users))
