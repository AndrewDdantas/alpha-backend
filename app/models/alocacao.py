from datetime import datetime, time
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Time
from sqlalchemy.orm import relationship

from app.db.base import Base


class AlocacaoDiaria(Base):
    """Alocação de veículos para uma diária específica."""

    __tablename__ = "alocacoes_diarias"

    id = Column(Integer, primary_key=True, index=True)
    diaria_id = Column(Integer, ForeignKey("diarias.id"), nullable=False)
    veiculo_id = Column(Integer, ForeignKey("veiculos.id"), nullable=False)
    rota_id = Column(Integer, ForeignKey("rotas.id"), nullable=True)
    horario_saida = Column(Time, nullable=True)
    observacao = Column(String(500), nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    diaria = relationship("Diaria", backref="alocacoes")
    veiculo = relationship("Veiculo")
    rota = relationship("Rota")
    colaboradores = relationship("AlocacaoColaborador", back_populates="alocacao_diaria", cascade="all, delete-orphan")


class AlocacaoColaborador(Base):
    """Alocação de um colaborador a um veículo específico."""

    __tablename__ = "alocacoes_colaboradores"

    id = Column(Integer, primary_key=True, index=True)
    alocacao_diaria_id = Column(Integer, ForeignKey("alocacoes_diarias.id"), nullable=False)
    inscricao_id = Column(Integer, ForeignKey("inscricoes.id"), nullable=False)
    ponto_parada_id = Column(Integer, ForeignKey("pontos_parada.id"), nullable=True)
    horario_estimado = Column(Time, nullable=True)  # Horário de passagem no ponto
    ordem_embarque = Column(Integer, default=0)  # Ordem de embarque na rota
    criado_em = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    alocacao_diaria = relationship("AlocacaoDiaria", back_populates="colaboradores")
    inscricao = relationship("Inscricao", backref="alocacao")
    ponto_parada = relationship("PontoParada")
