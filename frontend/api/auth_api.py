from typing import Any

import requests

from frontend.api.api_client import build_api_url
from frontend.exceptions import (
    ApiException,
    UnauthorizedException,
    UserNotActiveException,
    UserAlreadyExistsException,
    EmailAlreadyExistsException,
)


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
            body = response.json()
            error_code = body.get("error", "")
            if error_code == "USER_NOT_ACTIVATE":
                raise UserNotActiveException(body.get("message", "Usuario no activo. Contacta al administrador."))
            raise UnauthorizedException(body.get("message", "Credenciales inválidas"))

        response.raise_for_status()
        return response.json()

    def register(
        self,
        email: str,
        document: str,
        username: str,
        password: str
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
                },
                timeout=30,
            )
        except requests.RequestException as e:
            raise ApiException(f"Error de conexión: {e}")

        if response.status_code == 409:
            body = response.json()
            error_code = body.get("error", "")
            msg = body.get("message", "El usuario ya existe")
            if error_code == "EMAIL_ALREADY_EXISTS":
                raise EmailAlreadyExistsException(msg)
            raise UserAlreadyExistsException(msg)

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

    def change_password(self, new_password: str, token: str) -> dict[str, Any]:
        url = build_api_url("auth/change-password")
        try:
            response = requests.post(
                url,
                json={"new_password": new_password},
                headers={"Authorization": f"Bearer {token}"},
                timeout=30,
            )
        except requests.RequestException as e:
            raise ApiException(f"Error de conexión: {e}")

        if response.status_code == 400:
            body = response.json()
            raise ApiException(body.get("message", "Contraseña inválida"), status_code=400)

        response.raise_for_status()
        return response.json()

    def admin_reset_password(self, user_id: int, new_password: str | None, token: str) -> dict[str, Any]:
        url = build_api_url("auth/admin/reset-password")
        try:
            response = requests.post(
                url,
                json={"user_id": user_id, "new_password": new_password},
                headers={"Authorization": f"Bearer {token}"},
                timeout=30,
            )
        except requests.RequestException as e:
            raise ApiException(f"Error de conexión: {e}")

        if response.status_code == 403:
            raise ApiException("No tienes permisos para esta acción", status_code=403)

        response.raise_for_status()
        return response.json()
