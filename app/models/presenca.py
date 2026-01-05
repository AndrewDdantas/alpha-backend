"""Modelo de Registro de Presença."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class RegistroPresenca(Base):
    """Registro de presença com foto de um colaborador em uma diária."""

    __tablename__ = "registros_presenca"

    id = Column(Integer, primary_key=True, index=True)
    foto_url = Column(String(500), nullable=False)  # URL da foto de presença
    horario_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
    latitude = Column(Float, nullable=True)  # GPS opcional
    longitude = Column(Float, nullable=True)
    observacao = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    # Foreign Keys
    inscricao_id = Column(Integer, ForeignKey("inscricoes.id"), nullable=False)
    registrado_por_id = Column(Integer, ForeignKey("pessoas.id"), nullable=False)  # Supervisor

    # Relacionamentos
    inscricao = relationship("Inscricao", backref="registro_presenca")
    registrado_por = relationship("Pessoa", foreign_keys=[registrado_por_id], backref="presencas_registradas")
