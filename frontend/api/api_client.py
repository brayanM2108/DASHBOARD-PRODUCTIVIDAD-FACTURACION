import os
from urllib.parse import urljoin

import requests
import streamlit as st


def get_api_base() -> str:
    try:
        configured_base = st.secrets.get("API_BASE")
    except Exception:
        configured_base = None
    return configured_base or os.getenv("API_BASE", "http://localhost:8000")


def build_api_url(path: str) -> str:
    base_url = get_api_base().rstrip("/")
    normalized_path = path.lstrip("/")

    if normalized_path.startswith("api/"):
        normalized_path = normalized_path.removeprefix("api/")

    if not base_url.endswith("/api"):
        base_url = f"{base_url}/api"

    return urljoin(f"{base_url}/", normalized_path)


class ApiClient:

    def __init__(self):
        self.base_url = get_api_base()

    def _headers(self) -> dict:
        token = st.session_state.get("token")
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}

    def get(self, path: str, params: dict | None = None) -> dict:
        url = build_api_url(path)
        response = requests.get(
            url,
            params=params,
            headers=self._headers(),
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def post(self, path: str, json: dict | None = None) -> dict:
        url = build_api_url(path)
        response = requests.post(
            url,
            json=json,
            headers=self._headers(),
            timeout=30,
        )
        response.raise_for_status()
        return response.json()