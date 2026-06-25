from typing import Any

import requests
from frontend.api.api_client import build_api_url
from frontend.exceptions import ApiException, UnauthorizedException


class ProcessConfigApi:

    def __init__(self, token: str | None = None):
        self.token = token

    def _headers(self) -> dict:
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    def _request(self, method: str, path: str, json: dict | None = None) -> dict[str, Any]:
        url = build_api_url(path)
        try:
            response = requests.request(
                method,
                url,
                json=json,
                headers=self._headers(),
                timeout=30,
            )
        except requests.RequestException as e:
            raise ApiException(f"Connection error: {e}")

        if response.status_code == 401:
            raise UnauthorizedException()
        response.raise_for_status()
        return response.json()

    def get_config(self) -> dict[str, Any]:
        return self._request("GET", "admin/process-config")

    def update_config(self, processes: list[dict], module_times: dict | None = None) -> dict[str, Any]:
        body = {"processes": processes}
        if module_times is not None:
            body["module_times"] = module_times
        return self._request("PUT", "admin/process-config", json=body)
