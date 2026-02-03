from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SqlEnum, ForeignKey, Date, Text
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.enums import TipoPessoa
from app.models.perfil import pessoa_perfil


class Pessoa(Base):
    """Modelo de Pessoa no banco de dados."""

    __tablename__ = "pessoas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    cpf = Column(String(14), unique=True, index=True, nullable=False)
    pis = Column(String(14), unique=True, index=True, nullable=False)  # PIS/PASEP
    telefone = Column(String(20), nullable=True)
    data_nascimento = Column(DateTime, nullable=True)
    endereco = Column(String(255), nullable=True)
    complemento = Column(String(100), nullable=True)  # Complemento do endereço
    cidade = Column(String(100), nullable=True)
    estado = Column(String(2), nullable=True)
    cep = Column(String(10), nullable=True)
    senha_hash = Column(String(255), nullable=True)
    tipo_pessoa = Column(SqlEnum(TipoPessoa), default=TipoPessoa.COLABORADOR, nullable=False)
    ativo = Column(Boolean, default=True)
    foto_url = Column(String(500), nullable=True)  # URL da foto de perfil
    
    # Campos de bloqueio
    bloqueado = Column(Boolean, default=False)
    motivo_bloqueio = Column(Text, nullable=True)
    bloqueado_ate = Column(Date, nullable=True)  # Bloqueio temporário
    
    # Campos de recuperação de senha
    reset_token = Column(String(255), nullable=True, index=True)
    reset_token_expires = Column(DateTime, nullable=True)
    
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Ponto de embarque do fretado
    ponto_parada_id = Column(Integer, ForeignKey("pontos_parada.id"), nullable=True)

    # Relacionamentos
    ponto_parada = relationship("PontoParada", back_populates="pessoas")
    perfis = relationship(
        "Perfil", 
        secondary=pessoa_perfil,
        primaryjoin="Pessoa.id == pessoa_perfil.c.pessoa_id",
        secondaryjoin="Perfil.id == pessoa_perfil.c.perfil_id",
        backref="pessoas"
    )



