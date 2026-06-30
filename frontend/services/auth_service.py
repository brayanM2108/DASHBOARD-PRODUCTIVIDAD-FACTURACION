from datetime import datetime, timezone

import streamlit as st
from jose import jwt

from frontend.api.auth_api import AuthApi
from frontend.exceptions import ApiException
from frontend.models.auth import TokenResponse, User


class AuthFrontendService:

    def __init__(self):
        self.api = AuthApi()

    def login(self, email: str, password: str) -> TokenResponse:
        response = self.api.login(email, password)
        token_response = TokenResponse(
            access_token=response["access_token"],
            refresh_token=response["refresh_token"],
            token_type=response.get("token_type", "bearer"),
        )
        st.session_state["token"] = token_response.access_token
        st.session_state["refresh_token"] = token_response.refresh_token
        st.session_state["_just_logged_in"] = True
        try:
            payload = jwt.decode(token_response.access_token, key="", options={"verify_signature": False})
            st.session_state["token_exp"] = payload.get("exp")
        except Exception:
            st.session_state["token_exp"] = None
        if "user" in response:
            st.session_state["user"] = response["user"]
            st.session_state["must_change_password"] = response["user"].get("must_change_password", False)
        return token_response

    def register(
        self,
        email: str,
        username: str,
        document: str,
        password: str,
    ) -> None:
        self.api.register(email, document, username, password)

    def try_refresh_token(self) -> bool:
        refresh_token = st.session_state.get("refresh_token")
        if not refresh_token:
            print("[AUTH] No hay refresh_token en session_state")
            return False
        try:
            print("[AUTH] Intentando refresh token...")
            response = self.api.refresh(refresh_token)
            print("[AUTH] Refresh exitoso")
            st.session_state["token"] = response["access_token"]
            st.session_state["refresh_token"] = response["refresh_token"]
            try:
                payload = jwt.decode(response["access_token"], key="", options={"verify_signature": False})
                st.session_state["token_exp"] = payload.get("exp")
            except Exception:
                st.session_state["token_exp"] = None
            if "user" in response:
                st.session_state["user"] = response["user"]
                st.session_state["must_change_password"] = response["user"].get("must_change_password", False)
            return True
        except Exception as e:
            print(f"[AUTH] Error en refresh: {e}")
            return False

    def get_current_user(self) -> User | None:
        user_data = st.session_state.get("user")
        if not user_data:
            return None
        return User(
            id=user_data.get("id"),
            username=user_data.get("username"),
            email=user_data.get("email"),
            is_active=user_data.get("is_active", True),
        )

    def is_token_valid(self) -> bool:
        token = st.session_state.get("token")
        exp = st.session_state.get("token_exp")
        if not token:
            print("[AUTH] No hay token en session_state")
            return False
        if exp is None:
            print("[AUTH] No hay token_exp en session_state")
            return False
        is_valid = datetime.now(timezone.utc).timestamp() < exp
        print(f"[AUTH] Token válido: {is_valid}, exp: {exp}, now: {datetime.now(timezone.utc).timestamp()}")
        return is_valid

    def logout(self) -> None:
        token = st.session_state.get("token")
        if token:
            try:
                self.api.logout(token)
            except Exception:
                pass
        st.session_state.pop("token", None)
        st.session_state.pop("refresh_token", None)
        st.session_state.pop("user", None)
        st.session_state.pop("token_exp", None)
        st.session_state.pop("must_change_password", None)
        st.rerun()

    def change_password(self, new_password: str) -> None:
        token = st.session_state.get("token")
        if not token:
            raise ApiException("No hay token de autenticación")
        self.api.change_password(new_password, token)
        st.session_state["must_change_password"] = False

    def admin_reset_password(self, user_id: int, new_password: str | None = None) -> dict:
        token = st.session_state.get("token")
        if not token:
            raise ApiException("No hay token de autenticación")
        return self.api.admin_reset_password(user_id, new_password, token)
