"""Schemas Pydantic para Turno."""
from datetime import time, datetime
from typing import Optional, List

from pydantic import BaseModel, field_serializer


class TurnoBase(BaseModel):
    """Schema base para Turno."""
    nome: str
    hora_inicio: str  # HH:MM
    hora_fim: str     # HH:MM


class TurnoCreate(TurnoBase):
    """Schema para criação de Turno."""
    pass


class TurnoUpdate(BaseModel):
    """Schema para atualização de Turno."""
    nome: Optional[str] = None
    hora_inicio: Optional[str] = None
    hora_fim: Optional[str] = None
    ativo: Optional[bool] = None


class TurnoResponse(BaseModel):
    """Schema de resposta para Turno."""
    id: int
    empresa_id: int
    nome: str
    hora_inicio: time
    hora_fim: time
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    @field_serializer('hora_inicio', 'hora_fim')
    def serialize_time(self, v: time) -> str:
        return v.strftime('%H:%M') if v else None

    class Config:
        from_attributes = True


class TurnoList(BaseModel):
    """Lista de turnos."""
    total: int
    turnos: List[TurnoResponse]
