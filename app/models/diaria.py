from datetime import datetime, date, time
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date, Time, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SqlEnum

from app.db.base import Base
from app.models.enums import StatusDiaria, StatusInscricao


class Diaria(Base):
    """Modelo de Diária no banco de dados."""

    __tablename__ = "diarias"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(150), nullable=False)
    descricao = Column(Text, nullable=True)
    data = Column(Date, nullable=False, index=True)
    horario_inicio = Column(Time, nullable=True)
    horario_fim = Column(Time, nullable=True)
    vagas = Column(Integer, nullable=False, default=1)
    valor = Column(Numeric(10, 2), nullable=True)  # Valor da diária
    local = Column(String(255), nullable=True)
    observacoes = Column(Text, nullable=True)
    status = Column(SqlEnum(StatusDiaria), default=StatusDiaria.ABERTA, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign Keys
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    supervisor_id = Column(Integer, ForeignKey("pessoas.id"), nullable=True)  # Supervisor da diária

    # Relacionamentos
    empresa = relationship("Empresa", backref="diarias")
    supervisor = relationship("Pessoa", foreign_keys=[supervisor_id], backref="diarias_supervisionadas")
    inscricoes = relationship("Inscricao", back_populates="diaria", cascade="all, delete-orphan")

    @property
    def vagas_disponiveis(self) -> int:
        """Retorna o número de vagas disponíveis."""
        inscritos = len([i for i in self.inscricoes if i.status in [StatusInscricao.CONFIRMADA, StatusInscricao.PENDENTE]])
        return max(0, self.vagas - inscritos)


class Inscricao(Base):
    """Modelo de Inscrição em Diária."""

    __tablename__ = "inscricoes"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(SqlEnum(StatusInscricao), default=StatusInscricao.PENDENTE, nullable=False)
    observacao = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign Keys
    pessoa_id = Column(Integer, ForeignKey("pessoas.id"), nullable=False)
    diaria_id = Column(Integer, ForeignKey("diarias.id"), nullable=False)

    # Relacionamentos
    pessoa = relationship("Pessoa", backref="inscricoes")
    diaria = relationship("Diaria", back_populates="inscricoes")
