from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, field_validator


# ========== Schemas de Permissão ==========

class PermissaoBase(BaseModel):
    """Schema base para Permissão."""
    codigo: str
    nome: str
    descricao: Optional[str] = None
    recurso: str
    acao: str
    ativo: bool = True

    @field_validator("codigo", "recurso", "acao")
    @classmethod
    def nao_vazio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Campo obrigatório")
        return v.strip()


class PermissaoCreate(PermissaoBase):
    """Schema para criação de Permissão."""
    pass


class PermissaoUpdate(BaseModel):
    """Schema para atualização de Permissão."""
    nome: Optional[str] = None
    descricao: Optional[str] = None
    ativo: Optional[bool] = None


class PermissaoResponse(PermissaoBase):
    """Schema de resposta de Permissão."""
    id: int
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True


class PermissaoList(BaseModel):
    """Schema para lista de permissões."""
    items: List[PermissaoResponse]
    total: int


# ========== Schemas de Perfil ==========

class PerfilBase(BaseModel):
    """Schema base para Perfil."""
    nome: str
    codigo: str
    descricao: Optional[str] = None
    ativo: bool = True

    @field_validator("nome", "codigo")
    @classmethod
    def nao_vazio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Campo obrigatório")
        return v.strip()


class PerfilCreate(PerfilBase):
    """Schema para criação de Perfil."""
    permissoes_ids: List[int] = []


class PerfilUpdate(BaseModel):
    """Schema para atualização de Perfil."""
    nome: Optional[str] = None
    descricao: Optional[str] = None
    ativo: Optional[bool] = None
    permissoes_ids: Optional[List[int]] = None


class PerfilResponse(PerfilBase):
    """Schema de resposta de Perfil."""
    id: int
    sistema: bool
    permissoes: List[PermissaoResponse] = []
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True


class PerfilSimples(BaseModel):
    """Schema simplificado de Perfil (sem permissões)."""
    id: int
    nome: str
    codigo: str
    descricao: Optional[str] = None
    sistema: bool
    ativo: bool

    class Config:
        from_attributes = True


class PerfilList(BaseModel):
    """Schema para lista de perfis."""
    items: List[PerfilResponse]
    total: int


# ========== Schemas de Atribuição de Perfil ==========

class AtribuirPerfil(BaseModel):
    """Schema para atribuir perfil a um usuário."""
    pessoa_id: int
    perfil_id: int


class RemoverPerfil(BaseModel):
    """Schema para remover perfil de um usuário."""
    pessoa_id: int
    perfil_id: int


class UsuarioPerfis(BaseModel):
    """Schema para visualizar perfis de um usuário."""
    pessoa_id: int
    nome: str
    email: str
    tipo_pessoa: str
    perfis: List[PerfilSimples] = []

    class Config:
        from_attributes = True
