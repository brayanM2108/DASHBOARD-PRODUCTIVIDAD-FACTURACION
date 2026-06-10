from datetime import datetime, timezone

import streamlit as st
from jose import jwt

from frontend.api.auth_api import AuthApi
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
        if "user" in response:
            st.session_state["user"] = response["user"]
        return token_response

    def register(
        self,
        email: str,
        username: str,
        document: str,
        password: str,
        role: str | None = None,
    ) -> None:
        self.api.register(email, document, username, password, role)

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
            if "user" in response:
                st.session_state["user"] = response["user"]
            return True
        except Exception as e:
            print(f"[AUTH] Error en refresh: {e}")
            return False

    def get_current_user(self) -> User:
        user_data = st.session_state.get("user")
        if user_data:
            return User(
                id=user_data.get("id"),
                username=user_data.get("username"),
                email=user_data.get("email"),
                role=user_data.get("role"),
                is_active=user_data.get("is_active", True),
            )

        token = st.session_state.get("token")
        if not token:
            return User()
        
        try:
            payload = jwt.decode(token, key="", options={"verify_signature": False})
            username = payload.get("username")
            email = payload.get("sub")
            role = payload.get("role")
            
            if username:
                return User(email=email, username=username, role=role)
            
            if email:
                try:
                    user_response = self.api.me(token)
                    user_obj = User(
                        id=user_response.get("id"),
                        username=user_response.get("username"),
                        email=user_response.get("email"),
                        role=user_response.get("role"),
                        is_active=user_response.get("is_active", True),
                    )
                    st.session_state["user"] = {
                        "id": user_obj.id,
                        "username": user_obj.username,
                        "email": user_obj.email,
                        "role": user_obj.role,
                        "is_active": user_obj.is_active,
                    }
                    return user_obj
                except Exception:
                    return User(email=email)
            
            return User()
        except Exception:
            return User()

    def is_token_valid(self) -> bool:
        token = st.session_state.get("token")
        if not token:
            print("[AUTH] No hay token en session_state")
            return False
        try:
            payload = jwt.decode(token, key="", options={"verify_signature": False})
            exp = payload.get("exp")
            if exp is None:
                print("[AUTH] Token no tiene exp")
                return False
            is_valid = datetime.now(timezone.utc).timestamp() < exp
            print(f"[AUTH] Token válido: {is_valid}, exp: {exp}, now: {datetime.now(timezone.utc).timestamp()}")
            return is_valid
        except Exception as e:
            print(f"[AUTH] Error decodificando token: {e}")
            return False

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
        st.rerun()
