from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, field_validator


class EmpresaBase(BaseModel):
    """Schema base para Empresa."""

    nome: str
    cnpj: str
    razao_social: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    contato_nome: Optional[str] = None
    contato_telefone: Optional[str] = None


class EmpresaCreate(EmpresaBase):
    """Schema para criação de Empresa."""

    @field_validator("cnpj")
    @classmethod
    def cnpj_valido(cls, v: str) -> str:
        # Remove caracteres não numéricos
        cnpj = "".join(c for c in v if c.isdigit())
        if len(cnpj) != 14:
            raise ValueError("CNPJ deve ter 14 dígitos")
        return cnpj


class EmpresaUpdate(BaseModel):
    """Schema para atualização de Empresa."""

    nome: Optional[str] = None
    razao_social: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    contato_nome: Optional[str] = None
    contato_telefone: Optional[str] = None
    ativo: Optional[bool] = None


class EmpresaResponse(EmpresaBase):
    """Schema de resposta para Empresa."""

    id: int
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True


class EmpresaSimples(BaseModel):
    """Schema simplificado de Empresa."""

    id: int
    nome: str
    cnpj: str

    class Config:
        from_attributes = True


class EmpresaList(BaseModel):
    """Schema para listagem de Empresas."""

    total: int
    empresas: List[EmpresaResponse]
