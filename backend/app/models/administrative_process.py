from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .user import Base


class AdministrativeProcess(Base):
    __tablename__ = "administrative_processes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(Date, nullable=False, index=True)
    nombre = Column(String(255), nullable=False, index=True)
    documento = Column(String(100), nullable=False)
    proceso = Column(String(255), nullable=False, index=True)
    cantidad = Column(Integer, nullable=False)
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    usuario = relationship("User", backref="administrative_processes")
