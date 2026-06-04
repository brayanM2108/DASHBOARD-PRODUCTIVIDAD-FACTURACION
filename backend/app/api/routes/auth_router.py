from fastapi import APIRouter, Depends, HTTPException, status
from ...services.auth_service import AuthService
from ..schemas.auth import Token, LoginRequest, RegisterRequest
from ..schemas.user import UserOut
from ..deps import get_auth_service, get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post(
    "/login",
    response_model=Token,
)
def login(
        payload: LoginRequest,
        auth_service: AuthService = Depends(get_auth_service),
):
    token = auth_service.authenticate(payload.username, payload.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", response_model=Token)
def register(
        payload: RegisterRequest,
        auth_service: AuthService = Depends(get_auth_service),
):
    result = auth_service.register(payload.username, payload.password)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario ya existe"
        )
    _, token = result
    return {"access_token": token, "token_type": "bearer"}

@router.get(
    "/me",
    response_model=UserOut,
)
def me(
        current_user=Depends(get_current_user),
):

    return current_user