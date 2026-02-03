from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel

from app.models.enums import StatusDiaria, StatusInscricao
from app.schemas.empresa import EmpresaSimples


# ========== Inscrição Schemas ==========

class InscricaoBase(BaseModel):
    """Schema base para Inscrição."""

    observacao: Optional[str] = None


class InscricaoCreate(InscricaoBase):
    """Schema para criar inscrição."""

    diaria_id: int


class InscricaoUpdate(BaseModel):
    """Schema para atualizar inscrição (admin)."""

    status: Optional[StatusInscricao] = None
    observacao: Optional[str] = None


class PessoaSimples(BaseModel):
    """Schema simplificado de Pessoa para inscrições."""

    id: int
    nome: str
    email: str
    telefone: Optional[str] = None

    class Config:
        from_attributes = True


class InscricaoResponse(InscricaoBase):
    """Schema de resposta para Inscrição."""

    id: int
    status: StatusInscricao
    pessoa_id: int
    diaria_id: int
    criado_em: datetime

    class Config:
        from_attributes = True


class InscricaoComPessoa(InscricaoResponse):
    """Inscrição com dados da pessoa (para admin ver inscritos)."""

    pessoa: PessoaSimples


class InscricaoManual(BaseModel):
    """Schema para inscrição manual feita pelo gestor."""

    pessoa_id: int
    ignorar_intersticio: bool = False


# ========== Diária Schemas ==========

class DiariaBase(BaseModel):
    """Schema base para Diária."""

    titulo: str
    descricao: Optional[str] = None
    data: date
    horario_inicio: Optional[time] = None
    horario_fim: Optional[time] = None
    vagas: int = 1
    valor: Optional[Decimal] = None
    local: Optional[str] = None
    observacoes: Optional[str] = None


class DiariaCreate(DiariaBase):
    """Schema para criação de Diária."""

    empresa_id: int
    supervisor_id: Optional[int] = None


class DiariaUpdate(BaseModel):
    """Schema para atualização de Diária."""

    titulo: Optional[str] = None
    descricao: Optional[str] = None
    data: Optional[date] = None
    horario_inicio: Optional[time] = None
    horario_fim: Optional[time] = None
    vagas: Optional[int] = None
    valor: Optional[Decimal] = None
    local: Optional[str] = None
    observacoes: Optional[str] = None
    status: Optional[StatusDiaria] = None
    supervisor_id: Optional[int] = None


class SupervisorSimples(BaseModel):
    """Schema simplificado de Supervisor."""

    id: int
    nome: str
    telefone: Optional[str] = None

    class Config:
        from_attributes = True


class DiariaResponse(DiariaBase):
    """Schema de resposta para Diária."""

    id: int
    empresa_id: int
    supervisor_id: Optional[int] = None
    status: StatusDiaria
    vagas_disponiveis: int
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True


class DiariaComEmpresa(DiariaResponse):
    """Diária com dados da empresa e supervisor."""

    empresa: EmpresaSimples
    supervisor: Optional[SupervisorSimples] = None


class DiariaComInscricoes(DiariaComEmpresa):
    """Diária com lista de inscrições (para admin)."""

    inscricoes: List[InscricaoComPessoa] = []


class DiariaList(BaseModel):
    """Schema para listagem de Diárias."""

    total: int
    diarias: List[DiariaComEmpresa]


# ========== Minhas Inscrições ==========

class DiariaSimples(BaseModel):
    """Schema simplificado de Diária."""

    id: int
    titulo: str
    data: date
    horario_inicio: Optional[time] = None
    local: Optional[str] = None
    status: StatusDiaria
    empresa: EmpresaSimples

    class Config:
        from_attributes = True


class MinhaInscricao(BaseModel):
    """Schema para colaborador ver suas inscrições."""

    id: int
    status: StatusInscricao
    criado_em: datetime
    diaria: DiariaSimples

    class Config:
        from_attributes = True
