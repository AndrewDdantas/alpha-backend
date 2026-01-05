from datetime import datetime, time
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Time, Float
from sqlalchemy.orm import relationship

from app.db.base import Base


class Rota(Base):
    """Modelo de Rota de Fretado."""

    __tablename__ = "rotas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(String(255), nullable=True)
    horario_ida = Column(Time, nullable=True)
    horario_volta = Column(Time, nullable=True)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    pontos_parada = relationship("PontoParada", back_populates="rota", cascade="all, delete-orphan")


class PontoParada(Base):
    """Modelo de Ponto de Parada do Fretado."""

    __tablename__ = "pontos_parada"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    endereco = Column(String(255), nullable=True)
    referencia = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    horario = Column(Time, nullable=True)
    ordem = Column(Integer, default=0)  # Ordem do ponto na rota
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign Keys
    rota_id = Column(Integer, ForeignKey("rotas.id"), nullable=False)

    # Relacionamentos
    rota = relationship("Rota", back_populates="pontos_parada")
    pessoas = relationship("Pessoa", back_populates="ponto_parada")

