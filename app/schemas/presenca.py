"""Schemas para Registro de Presença."""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class RegistroPresencaBase(BaseModel):
    """Schema base para Registro de Presença."""
    
    foto_url: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    observacao: Optional[str] = None


class RegistroPresencaCreate(RegistroPresencaBase):
    """Schema para criação de registro de presença."""
    
    inscricao_id: int


class RegistroPresencaResponse(RegistroPresencaBase):
    """Schema de resposta para registro de presença."""
    
    id: int
    inscricao_id: int
    registrado_por_id: int
    horario_registro: datetime
    criado_em: datetime

    # Dados da pessoa presente
    pessoa_nome: Optional[str] = None
    pessoa_id: Optional[int] = None

    class Config:
        from_attributes = True


class InscritoPresenca(BaseModel):
    """Inscrito com status de presença."""
    
    inscricao_id: int
    pessoa_id: int
    pessoa_nome: str
    pessoa_telefone: Optional[str] = None
    status_inscricao: str
    presenca_registrada: bool = False
    horario_registro: Optional[datetime] = None
    foto_url: Optional[str] = None


class PresencaDiariaResponse(BaseModel):
    """Resumo de presenças de uma diária."""
    
    diaria_id: int
    diaria_titulo: str
    diaria_local: Optional[str] = None
    diaria_data: Optional[str] = None
    total_inscritos: int
    total_presentes: int
    inscritos: List[InscritoPresenca]  # Todos os inscritos
    presencas: List[RegistroPresencaResponse]  # Apenas registrados (retrocompat)

