from typing import Any

import requests

from frontend.api.api_client import build_api_url
from frontend.exceptions import ApiException, UnauthorizedException


class AuthApi:

    def login(self, email: str, password: str) -> dict[str, Any]:
        url = build_api_url("auth/login")
        try:
            response = requests.post(
                url,
                json={"email": email, "password": password},
                timeout=30,
            )
        except requests.RequestException as e:
            raise ApiException(f"Error de conexión: {e}")

        if response.status_code == 401:
            raise UnauthorizedException("Credenciales inválidas")

        response.raise_for_status()
        return response.json()

    def register(
        self,
        email: str,
        document: str,
        username: str,
        password: str,
        role: str | None = None,
    ) -> dict[str, Any]:
        url = build_api_url("auth/register")
        try:
            response = requests.post(
                url,
                json={
                    "email": email,
                    "document": document,
                    "username": username,
                    "password": password,
                    "role": role,
                },
                timeout=30,
            )
        except requests.RequestException as e:
            raise ApiException(f"Error de conexión: {e}")

        if response.status_code == 409:
            raise ApiException("El usuario ya existe", status_code=409)

        response.raise_for_status()
        return response.json()

    def refresh(self, refresh_token: str) -> dict[str, Any]:
        url = build_api_url("auth/refresh")
        try:
            response = requests.post(
                url,
                json={"refresh_token": refresh_token},
                timeout=30,
            )
        except requests.RequestException as e:
            raise ApiException(f"Error de conexión: {e}")

        if response.status_code == 401:
            raise UnauthorizedException("Refresh token inválido o expirado")

        response.raise_for_status()
        return response.json()

    def me(self, token: str) -> dict[str, Any]:
        url = build_api_url("auth/me")
        try:
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
                timeout=30,
            )
        except requests.RequestException as e:
            raise ApiException(f"Error de conexión: {e}")

        if response.status_code == 401:
            raise UnauthorizedException("Token inválido o expirado")

        response.raise_for_status()
        return response.json()

    def logout(self, token: str) -> dict[str, Any]:
        url = build_api_url("auth/logout")
        try:
            response = requests.post(
                url,
                headers={"Authorization": f"Bearer {token}"},
                timeout=30,
            )
        except requests.RequestException as e:
            raise ApiException(f"Error de conexión: {e}")

        response.raise_for_status()
        return response.json()
