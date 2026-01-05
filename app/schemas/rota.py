from datetime import datetime, time
from typing import Optional, List, Union

from pydantic import BaseModel, field_serializer


# ========== Ponto de Parada Schemas ==========

class PontoParadaBase(BaseModel):
    """Schema base para Ponto de Parada."""

    nome: str
    endereco: Optional[str] = None
    referencia: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    horario: Optional[str] = None  # Aceita string HH:MM
    ordem: int = 0


class PontoParadaCreate(PontoParadaBase):
    """Schema para criação de Ponto de Parada."""

    rota_id: Optional[int] = None  # Pode ser passado pela URL


class PontoParadaUpdate(BaseModel):
    """Schema para atualização de Ponto de Parada."""

    nome: Optional[str] = None
    endereco: Optional[str] = None
    referencia: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    horario: Optional[str] = None
    ordem: Optional[int] = None
    ativo: Optional[bool] = None


class PontoParadaResponse(BaseModel):
    """Schema de resposta para Ponto de Parada."""

    id: int
    nome: str
    endereco: Optional[str] = None
    referencia: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    horario: Optional[Union[str, time]] = None
    ordem: int
    rota_id: int
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    @field_serializer('horario')
    def serialize_horario(self, v):
        if isinstance(v, time):
            return v.strftime('%H:%M')
        return v

    class Config:
        from_attributes = True


class PontoParadaSimples(BaseModel):
    """Schema simplificado para listagem."""

    id: int
    nome: str
    endereco: Optional[str] = None
    horario: Optional[Union[str, time]] = None
    ordem: int

    @field_serializer('horario')
    def serialize_horario(self, v):
        if isinstance(v, time):
            return v.strftime('%H:%M')
        return v

    class Config:
        from_attributes = True


# ========== Rota Schemas ==========

class RotaBase(BaseModel):
    """Schema base para Rota."""

    nome: str
    descricao: Optional[str] = None
    horario_ida: Optional[str] = None
    horario_volta: Optional[str] = None


class RotaCreate(RotaBase):
    """Schema para criação de Rota."""

    pass


class RotaUpdate(BaseModel):
    """Schema para atualização de Rota."""

    nome: Optional[str] = None
    descricao: Optional[str] = None
    horario_ida: Optional[str] = None
    horario_volta: Optional[str] = None
    ativo: Optional[bool] = None


class RotaResponse(BaseModel):
    """Schema de resposta para Rota."""

    id: int
    nome: str
    descricao: Optional[str] = None
    horario_ida: Optional[Union[str, time]] = None
    horario_volta: Optional[Union[str, time]] = None
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    @field_serializer('horario_ida', 'horario_volta')
    def serialize_horarios(self, v):
        if isinstance(v, time):
            return v.strftime('%H:%M')
        return v

    class Config:
        from_attributes = True


class RotaComPontos(RotaResponse):
    """Schema de Rota com seus pontos de parada."""

    pontos_parada: List[PontoParadaSimples] = []


class RotaList(BaseModel):
    """Schema para listagem de Rotas."""

    total: int
    rotas: List[RotaResponse]

