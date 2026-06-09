from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from ..models import AdministrativeProcess


class AdministrativeProcessRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, fecha: date, nombre: str, documento: str, proceso: str, cantidad: int, usuario_id: int) -> AdministrativeProcess:
        record = AdministrativeProcess(
            fecha=fecha,
            nombre=nombre,
            documento=documento,
            proceso=proceso,
            cantidad=cantidad,
            usuario_id=usuario_id,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_by_id(self, process_id: int) -> Optional[AdministrativeProcess]:
        return self.db.query(AdministrativeProcess).filter(AdministrativeProcess.id == process_id).first()

    def list(
        self,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        nombre: Optional[str] = None,
        proceso: Optional[str] = None,
        skip: int = 0,
        limit: int = 1000,
    ) -> list[AdministrativeProcess]:
        query = self.db.query(AdministrativeProcess)

        if fecha_desde:
            query = query.filter(AdministrativeProcess.fecha >= fecha_desde)
        if fecha_hasta:
            query = query.filter(AdministrativeProcess.fecha <= fecha_hasta)
        if nombre:
            query = query.filter(AdministrativeProcess.nombre == nombre)
        if proceso:
            query = query.filter(AdministrativeProcess.proceso == proceso)

        return query.offset(skip).limit(limit).all()

    def count(
        self,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        nombre: Optional[str] = None,
        proceso: Optional[str] = None,
    ) -> int:
        query = self.db.query(AdministrativeProcess)

        if fecha_desde:
            query = query.filter(AdministrativeProcess.fecha >= fecha_desde)
        if fecha_hasta:
            query = query.filter(AdministrativeProcess.fecha <= fecha_hasta)
        if nombre:
            query = query.filter(AdministrativeProcess.nombre == nombre)
        if proceso:
            query = query.filter(AdministrativeProcess.proceso == proceso)

        return query.count()

    def update(self, process_id: int, **kwargs) -> Optional[AdministrativeProcess]:
        record = self.get_by_id(process_id)
        if not record:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(record, key):
                setattr(record, key, value)
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, process_id: int) -> bool:
        record = self.get_by_id(process_id)
        if not record:
            return False
        self.db.delete(record)
        self.db.commit()
        return True
