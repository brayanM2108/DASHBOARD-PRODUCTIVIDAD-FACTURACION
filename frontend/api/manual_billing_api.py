from typing import Any, Optional

import requests
import streamlit as st

from frontend.api.api_client import build_api_url
from frontend.exceptions import ApiException


class ManualBillingApi:

    def _headers(self) -> dict:
        token = st.session_state.get("token")
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}

    def list_processes(
        self,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        proceso: Optional[str] = None,
        skip: int = 0,
        limit: int = 10000,
    ) -> list[dict]:
        url = build_api_url("administrative-processes/")
        params: dict = {"skip": skip, "limit": limit}
        if fecha_desde:
            params["fecha_desde"] = fecha_desde
        if fecha_hasta:
            params["fecha_hasta"] = fecha_hasta
        if proceso:
            params["proceso"] = proceso
        try:
            resp = requests.get(url, params=params, headers=self._headers(), timeout=30)
        except requests.RequestException as e:
            raise ApiException(f"Error de conexión: {e}")
        resp.raise_for_status()
        return resp.json()

    def get_summary(
        self,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        proceso: Optional[str] = None,
    ) -> dict[str, Any]:
        url = build_api_url("administrative-processes/summary/global")
        params: dict = {}
        if fecha_desde:
            params["fecha_desde"] = fecha_desde
        if fecha_hasta:
            params["fecha_hasta"] = fecha_hasta
        if proceso:
            params["proceso"] = proceso
        try:
            resp = requests.get(url, params=params, headers=self._headers(), timeout=30)
        except requests.RequestException as e:
            raise ApiException(f"Error de conexión: {e}")
        resp.raise_for_status()
        return resp.json()

    def create_process(self, payload: dict) -> dict[str, Any]:
        url = build_api_url("administrative-processes/")
        try:
            resp = requests.post(url, json=payload, headers=self._headers(), timeout=30)
        except requests.RequestException as e:
            raise ApiException(f"Error de conexión: {e}")
        resp.raise_for_status()
        return resp.json()

    def update_process(self, process_id: int, payload: dict) -> dict[str, Any]:
        url = build_api_url(f"administrative-processes/{process_id}")
        try:
            resp = requests.put(url, json=payload, headers=self._headers(), timeout=30)
        except requests.RequestException as e:
            raise ApiException(f"Error de conexión: {e}")
        resp.raise_for_status()
        return resp.json()

    def delete_process(self, process_id: int) -> None:
        url = build_api_url(f"administrative-processes/{process_id}")
        try:
            resp = requests.delete(url, headers=self._headers(), timeout=30)
        except requests.RequestException as e:
            raise ApiException(f"Error de conexión: {e}")
        if resp.status_code == 404:
            raise ApiException("Registro no encontrado", status_code=404)
        resp.raise_for_status()
