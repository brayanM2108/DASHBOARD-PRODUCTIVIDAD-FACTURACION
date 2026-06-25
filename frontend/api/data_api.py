import requests
import streamlit as st

from frontend.api.api_client import build_api_url


class DataApi:

    @staticmethod
    def _headers() -> dict:
        token = st.session_state.get("token")
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}

    def upload(self, file_bytes: bytes, filename: str, module_key: str) -> dict:
        url = build_api_url("data/upload")
        response = requests.post(
            url,
            files={"file": (filename, file_bytes)},
            data={"module_key": module_key},
            headers=self._headers(),
            timeout=600,
        )
        response.raise_for_status()
        return response.json()

    def upload_billers(self, file_bytes: bytes, filename: str) -> dict:
        url = build_api_url("data/upload/billers")
        response = requests.post(
            url,
            files={"file": (filename, file_bytes)},
            headers=self._headers(),
            timeout=120,
        )
        response.raise_for_status()
        return response.json()

    def load(self, include_data: bool = False) -> dict:
        url = build_api_url(f"data/load?include_data={'true' if include_data else 'false'}")
        response = requests.get(
            url,
            headers=self._headers(),
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def load_dataset(self, dataset_key: str) -> dict:
        url = build_api_url(f"data/load/{dataset_key}")
        response = requests.get(
            url,
            headers=self._headers(),
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def delete(self, file_key: str) -> dict:
        url = build_api_url(f"data/{file_key}")
        response = requests.delete(
            url,
            headers=self._headers(),
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
