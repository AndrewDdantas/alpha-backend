from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Table, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


# Tabela associativa entre Perfis e Permissões
perfil_permissao = Table(
    'perfil_permissao',
    Base.metadata,
    Column('perfil_id', Integer, ForeignKey('perfis.id'), primary_key=True),
    Column('permissao_id', Integer, ForeignKey('permissoes.id'), primary_key=True)
)


# Tabela associativa entre Pessoas e Perfis
pessoa_perfil = Table(
    'pessoa_perfil',
    Base.metadata,
    Column('pessoa_id', Integer, ForeignKey('pessoas.id'), primary_key=True),
    Column('perfil_id', Integer, ForeignKey('perfis.id'), primary_key=True),
    Column('atribuido_em', DateTime, default=datetime.utcnow),
    Column('atribuido_por_id', Integer, ForeignKey('pessoas.id'), nullable=True)
)


class Permissao(Base):
    """Modelo de Permissão - representa uma ação específica em um recurso do sistema."""

    __tablename__ = "permissoes"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(100), unique=True, nullable=False, index=True)  # Ex: "diarias.create", "usuarios.read"
    nome = Column(String(100), nullable=False)  # Nome descritivo
    descricao = Column(Text, nullable=True)  # Descrição da permissão
    recurso = Column(String(50), nullable=False, index=True)  # Ex: "diarias", "usuarios", "relatorios"
    acao = Column(String(50), nullable=False)  # Ex: "create", "read", "update", "delete", "manage"
    ativo = Column(Boolean, default=True)
    
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    perfis = relationship("Perfil", secondary=perfil_permissao, back_populates="permissoes")

    def __repr__(self):
        return f"<Permissao {self.codigo}>"


class Perfil(Base):
    """Modelo de Perfil - agrupa permissões que podem ser atribuídas a usuários."""

    __tablename__ = "perfis"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=True, nullable=False, index=True)  # Ex: "Administrador", "Gestor de Frota"
    descricao = Column(Text, nullable=True)  # Descrição do perfil
    codigo = Column(String(50), unique=True, nullable=False, index=True)  # Código único (slug)
    sistema = Column(Boolean, default=False)  # Se True, não pode ser excluído (perfis padrão)
    ativo = Column(Boolean, default=True)
    
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    permissoes = relationship("Permissao", secondary=perfil_permissao, back_populates="perfis")
    # pessoas = relationship("Pessoa", secondary=pessoa_perfil, back_populates="perfis")

    def __repr__(self):
        return f"<Perfil {self.nome}>"
