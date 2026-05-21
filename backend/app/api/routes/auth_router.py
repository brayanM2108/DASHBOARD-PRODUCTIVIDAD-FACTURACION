from fastapi import (APIRouter,Depends,HTTPException,status)
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.auth_service import AuthService
from app.api.schemas.auth import (Token,LoginRequest,RegisterRequest)
from app.api.schemas.user import UserOut
from app.api.routes.deps import get_auth_service,get_current_user

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
        db: Session = Depends(get_db),
        auth_service: AuthService = Depends(get_auth_service),
):
    token = auth_service.authenticate(db, payload.username, payload.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", response_model=Token)
def register(
        payload: RegisterRequest,
        db: Session = Depends(get_db),
        auth_service: AuthService = Depends(get_auth_service),
):
    result = auth_service.register(db, payload.username, payload.password)
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