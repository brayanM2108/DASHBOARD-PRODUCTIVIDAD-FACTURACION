from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from ...services.auth_service import AuthService
from ..schemas.auth import Token, LoginRequest, RegisterRequest, RefreshTokenRequest
from ..schemas.user import UserOut
from ..deps import get_auth_service, get_current_user
from ...core.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@router.post("/login", response_model=Token)
def login(
    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    user, access_token, refresh_token = auth_service.authenticate(
        payload.email, payload.password
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "document": user.document,
            "role": user.role,
            "is_active": user.is_active,
        },
    }


@router.post("/register", response_model=Token)
def register(
    payload: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    user, access_token, refresh_token = auth_service.register(
        email=payload.email,
        document=payload.document,
        username=payload.username,
        password=payload.password,
        role=payload.role,
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
        },
    }


@router.post("/refresh", response_model=Token)
def refresh(
    payload: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    print(f"[AUTH_ROUTER] Recibida petición de refresh")
    try:
        user, access_token, refresh_token = auth_service.refresh(payload.refresh_token)
        print(f"[AUTH_ROUTER] Refresh exitoso para usuario: {user.username}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
            },
        }
    except Exception as e:
        print(f"[AUTH_ROUTER] Error en refresh: {type(e).__name__}: {e}")
        raise


@router.post("/logout")
def logout(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        email = payload.get("sub")
        if email:
            auth_service.revoke_refresh_token(email)
    except Exception:
        pass
    return {"message": "Sesión cerrada correctamente"}


@router.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_user)):
    return current_user
