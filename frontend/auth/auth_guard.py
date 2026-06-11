import streamlit as st

from frontend.services.auth_service import AuthFrontendService


def is_authenticated() -> bool:
    token = st.session_state.get("token")
    if not token:
        print("[AUTH_GUARD] No hay token")
        return False

    # Si acaba de hacer login, no intentar refresh
    # Mantener el flag para múltiples ejecuciones de Streamlit
    if st.session_state.get("_just_logged_in"):
        print("[AUTH_GUARD] Just logged in, skipping validation")
        # No eliminar el flag aquí, se eliminará cuando se navegue
        return True

    service = AuthFrontendService()

    if service.is_token_valid():
        print("[AUTH_GUARD] Token válido, acceso permitido")
        return True

    print("[AUTH_GUARD] Token inválido, intentando refresh")
    if service.try_refresh_token():
        print("[AUTH_GUARD] Refresh exitoso")
        return True

    print("[AUTH_GUARD] Refresh fallido, limpiando sesión")
    st.session_state.pop("token", None)
    st.session_state.pop("refresh_token", None)
    st.session_state.pop("user", None)
    st.session_state.pop("_just_logged_in", None)
    return False
