import requests
import streamlit as st

from frontend.api.api_client import build_api_url


class BillersAdminApi:

    @staticmethod
    def _headers() -> dict:
        token = st.session_state.get("token")
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}

    def list_billers(self) -> dict:
        url = build_api_url("admin/billers")
        response = requests.get(url, headers=self._headers(), timeout=30)
        response.raise_for_status()
        return response.json()

    def update_billers(self, facturadores: list[dict]) -> dict:
        url = build_api_url("admin/billers")
        response = requests.put(
            url,
            json={"facturadores": facturadores},
            headers=self._headers(),
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
