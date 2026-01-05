"""Modelo para Turnos de trabalho por Empresa."""
from datetime import datetime, time
from sqlalchemy import Column, Integer, String, Time, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class Turno(Base):
    """Turno de trabalho padrão de uma empresa."""

    __tablename__ = "turnos"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False)
    nome = Column(String(100), nullable=False)  # Ex: "Manhã", "Tarde", "Noite"
    hora_inicio = Column(Time, nullable=False)
    hora_fim = Column(Time, nullable=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    empresa = relationship("Empresa", back_populates="turnos")
