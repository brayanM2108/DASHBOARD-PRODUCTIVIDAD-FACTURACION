from fastapi import Depends

from ...repositories.administrative_process_repository import AdministrativeProcessRepository
from ...repositories.user_repository import UserRepository
from ...repositories.parquet_repository import ParquetRepository

from ...services.auth_service import AuthService
from ...services.billing_electronic_service import ElectronicBillingService
from ...services.productivity_service import ProductivityService
from ...services.legalizations_service import LegalizationsService
from ...services.manual_billing_service import ManualBillingService
from ...services.rips_service import RipsService
from ...services.radicacion_service import RadicacionService

from .repository_deps import (
    get_user_repository,
    get_legalizations_repository,
    get_electronic_billing_repository,
    get_administrative_process_repository,
    get_rips_repository,
    get_radicacion_repository,
)


def get_productivity_service() -> ProductivityService:
    return ProductivityService()


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repo)


def get_legalizations_service(
    repository: ParquetRepository = Depends(get_legalizations_repository),
    productivity_service: ProductivityService = Depends(get_productivity_service),
) -> LegalizationsService:
    return LegalizationsService(
        repository=repository,
        productivity_service=productivity_service,
    )


def get_rips_service(
    repository: ParquetRepository = Depends(get_rips_repository),
    productivity_service: ProductivityService = Depends(get_productivity_service),
) -> RipsService:
    return RipsService(
        repository=repository,
        productivity_service=productivity_service,
    )


def get_electronic_billing_service(
    repository: ParquetRepository = Depends(get_electronic_billing_repository),
    productivity_service: ProductivityService = Depends(get_productivity_service),
) -> ElectronicBillingService:
    return ElectronicBillingService(
        repository=repository,
        productivity_service=productivity_service,
    )


def get_manual_billing_service(
    repository: AdministrativeProcessRepository = Depends(get_administrative_process_repository),
) -> ManualBillingService:
    return ManualBillingService(repository)


def get_radicacion_service(
    repository: ParquetRepository = Depends(get_radicacion_repository),
) -> RadicacionService:
    return RadicacionService(repository=repository)
