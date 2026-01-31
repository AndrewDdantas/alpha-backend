from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class VeiculoBase(BaseModel):
    """Schema base para Veículo."""

    placa: str
    modelo: str
    capacidade: int
    tipo: Optional[str] = "van"
    cor: Optional[str] = None
    ano: Optional[int] = None
    motorista: Optional[str] = None
    telefone_motorista: Optional[str] = None


class VeiculoCreate(VeiculoBase):
    """Schema para criação de Veículo."""

    pass


class VeiculoUpdate(BaseModel):
    """Schema para atualização de Veículo."""

    placa: Optional[str] = None
    modelo: Optional[str] = None
    capacidade: Optional[int] = None
    tipo: Optional[str] = None
    cor: Optional[str] = None
    ano: Optional[int] = None
    motorista: Optional[str] = None
    telefone_motorista: Optional[str] = None
    ativo: Optional[bool] = None


class VeiculoResponse(VeiculoBase):
    """Schema de resposta para Veículo."""

    id: int
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True


class VeiculoList(BaseModel):
    """Schema para listagem de Veículos."""

    total: int
    veiculos: List[VeiculoResponse]
