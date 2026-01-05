from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.db.base import Base


class Empresa(Base):
    """Modelo de Empresa no banco de dados."""

    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    cnpj = Column(String(18), unique=True, index=True, nullable=False)
    razao_social = Column(String(200), nullable=True)
    email = Column(String(100), nullable=True)
    telefone = Column(String(20), nullable=True)
    endereco = Column(String(255), nullable=True)
    cidade = Column(String(100), nullable=True)
    estado = Column(String(2), nullable=True)
    cep = Column(String(10), nullable=True)
    contato_nome = Column(String(100), nullable=True)
    contato_telefone = Column(String(20), nullable=True)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    turnos = relationship("Turno", back_populates="empresa", cascade="all, delete-orphan")

