from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.db.base import Base


class Veiculo(Base):
    """Modelo de Veículo para transporte de fretado."""

    __tablename__ = "veiculos"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(10), unique=True, index=True, nullable=False)
    modelo = Column(String(100), nullable=False)
    capacidade = Column(Integer, nullable=False)  # Número de passageiros
    tipo = Column(String(50), default="van")  # van, micro-ônibus, ônibus
    cor = Column(String(50), nullable=True)
    ano = Column(Integer, nullable=True)
    motorista = Column(String(100), nullable=True)
    telefone_motorista = Column(String(20), nullable=True)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos futuros: alocações por rota/dia
