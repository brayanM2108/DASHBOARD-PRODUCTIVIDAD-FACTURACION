from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .user import Base


class AdministrativeProcess(Base):
    __tablename__ = "administrative_processes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(Date, nullable=False, index=True)
    proceso = Column(String(255), nullable=False, index=True)
    cantidad = Column(Integer, nullable=False)
    observacion = Column(Text, nullable=True)
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    usuario = relationship("User", backref="administrative_processes")

    @property
    def nombre(self):
        return self.usuario.username if self.usuario else ""

    @property
    def documento(self):
        return self.usuario.document if self.usuario else ""
