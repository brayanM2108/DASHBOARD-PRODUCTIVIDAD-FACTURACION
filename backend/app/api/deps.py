from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..core.config import settings
from ..utils.config.settings import FILES

from ..repositories.user_repository import UserRepository
from ..repositories.parquet_repository import ParquetRepository

from ..services.auth_service import AuthService
from ..services.billing_electronic_service import ElectronicBillingService
from ..services.productivity_service import ProductivityService
from ..services.legalizations_service import LegalizationsService


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)


# =====================================================
# REPOSITORIES
# =====================================================

def get_user_repository(
        db: Session = Depends(get_db)
):
    return UserRepository(db)


def get_legalizations_repository():
    return ParquetRepository(
        FILES["Legalizaciones"]
    )


def get_electronic_billing_repository():
    return ParquetRepository(
        FILES["FacturacionElectronica"]
    )


# =====================================================
# SERVICES
# =====================================================

def get_productivity_service():
    return ProductivityService()


def get_auth_service(
        user_repo: UserRepository = Depends(
            get_user_repository
        )
):
    return AuthService(user_repo)


def get_legalizations_service(
        repository: ParquetRepository = Depends(
            get_legalizations_repository
        ),
        productivity_service: ProductivityService = Depends(
            get_productivity_service
        ),
):
    return LegalizationsService(
        repository=repository,
        productivity_service=productivity_service,
    )


def get_electronic_billing_service(
        repository: ParquetRepository = Depends(
            get_electronic_billing_repository
        ),
        productivity_service: ProductivityService = Depends(
            get_productivity_service
        ),
):
    return ElectronicBillingService(
        repository=repository,
        productivity_service=productivity_service,
    )


# =====================================================
# AUTH
# =====================================================

def get_current_user(
        token: str = Depends(oauth2_scheme),
        user_repo: UserRepository = Depends(
            get_user_repository
        ),
):
    try:

        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        username = payload.get("sub")

        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    user = user_repo.get_by_username(username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )

    return user


# =====================================================
# ROLES
# =====================================================

def require_roles(*allowed_roles):

    def role_checker(
            current_user=Depends(get_current_user)
    ):

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No autorizado"
            )

        return current_user

    return role_checker
