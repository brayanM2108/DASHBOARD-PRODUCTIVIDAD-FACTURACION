from sqlalchemy.orm import Session
from fastapi import Depends

from ...db.session import get_db
from ...utils.config.settings import FILES
from ...repositories.user_repository import UserRepository
from ...repositories.parquet_repository import ParquetRepository
from ...repositories.administrative_process_repository import AdministrativeProcessRepository


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_administrative_process_repository(db: Session = Depends(get_db)) -> AdministrativeProcessRepository:
    return AdministrativeProcessRepository(db)


def get_legalizations_repository() -> ParquetRepository:
    return ParquetRepository(FILES["Legalizaciones"])


def get_electronic_billing_repository() -> ParquetRepository:
    return ParquetRepository(FILES["FacturacionElectronica"])
