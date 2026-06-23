from typing import Any

import requests
from frontend.api.api_client import build_api_url
from frontend.exceptions import ApiException, UnauthorizedException


class UsersApi:

    def __init__(self, token: str | None = None):
        self.token = token

    def _headers(self) -> dict:
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    def _request(self, method: str, path: str, json: dict | None = None, params: dict | None = None) -> dict[str, Any]:
        url = build_api_url(path)
        try:
            response = requests.request(
                method,
                url,
                json=json,
                params=params,
                headers=self._headers(),
                timeout=30,
            )
        except requests.RequestException as e:
            raise ApiException(f"Connection error: {e}")

        if response.status_code == 401:
            raise UnauthorizedException()
        response.raise_for_status()
        return response.json()

    def list_users(
        self,
        page: int = 1,
        size: int = 50,
        search: str | None = None,
        role_filter: str | None = None,
    ) -> dict[str, Any]:
        params = {"page": page, "size": size}
        if search:
            params["search"] = search
        if role_filter:
            params["role_filter"] = role_filter
        return self._request("GET", "users", params=params)

    def get_user(self, user_id: int) -> dict[str, Any]:
        return self._request("GET", f"users/{user_id}")

    def update_user(self, user_id: int, data: dict) -> dict[str, Any]:
        return self._request("PUT", f"users/{user_id}", json=data)

    def toggle_active(self, user_id: int) -> dict[str, Any]:
        return self._request("PATCH", f"users/{user_id}/toggle")
