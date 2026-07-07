from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, EmailStr, field_serializer

from app.models.enums import TipoPessoa


class PessoaBase(BaseModel):
    """Schema base para Pessoa."""

    nome: str
    email: EmailStr
    cpf: str
    pis: str  # PIS/PASEP obrigatório
    telefone: Optional[str] = None
    data_nascimento: Optional[datetime] = None
    endereco: Optional[str] = None
    complemento: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None


class PessoaCreate(PessoaBase):
    """Schema para criação de Pessoa."""

    senha: Optional[str] = None
    tipo_pessoa: TipoPessoa = TipoPessoa.COLABORADOR
    ponto_parada_id: Optional[int] = None
    foto_url: Optional[str] = None


class PessoaUpdate(BaseModel):
    """Schema para atualização de Pessoa (admin)."""

    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    pis: Optional[str] = None
    endereco: Optional[str] = None
    complemento: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    tipo_pessoa: Optional[TipoPessoa] = None
    ativo: Optional[bool] = None
    ponto_parada_id: Optional[int] = None
    bloqueado: Optional[bool] = None
    motivo_bloqueio: Optional[str] = None
    bloqueado_ate: Optional[date] = None


class PerfilUpdate(BaseModel):
    """Schema para atualização de perfil pelo próprio usuário.
    Apenas campos editáveis pelo usuário.
    """

    telefone: Optional[str] = None
    ponto_parada_id: Optional[int] = None
    foto_url: Optional[str] = None


class PessoaResponse(PessoaBase):
    """Schema de resposta para Pessoa."""

    id: int
    tipo_pessoa: TipoPessoa
    ativo: bool
    bloqueado: bool = False
    motivo_bloqueio: Optional[str] = None
    bloqueado_ate: Optional[date] = None
    ponto_parada_id: Optional[int] = None
    foto_url: Optional[str] = None
    criado_em: datetime
    atualizado_em: datetime

    @field_serializer("foto_url")
    def serialize_foto_url(self, value: Optional[str]) -> Optional[str]:
        if not value:
            return value
        from app.services.storage_service import storage_service

        return storage_service.resolve_access_url(value)

    class Config:
        from_attributes = True


class BloquearPessoa(BaseModel):
    """Schema para bloquear uma pessoa."""
    
    motivo: str
    bloqueado_ate: Optional[date] = None  # Se None, bloqueio permanente


class PessoaList(BaseModel):
    """Schema para listagem de Pessoas."""

    total: int
    pessoas: List[PessoaResponse]


