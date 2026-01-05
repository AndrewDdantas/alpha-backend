from datetime import datetime, time
from typing import Optional, List

from pydantic import BaseModel


# ========== Schemas de Alocação ==========

class AlocacaoColaboradorBase(BaseModel):
    """Base para alocação de colaborador."""
    inscricao_id: int
    ponto_parada_id: Optional[int] = None
    horario_estimado: Optional[str] = None
    ordem_embarque: int = 0


class AlocacaoColaboradorResponse(BaseModel):
    """Resposta de alocação de colaborador."""
    id: int
    inscricao_id: int
    ponto_parada_id: Optional[int] = None
    horario_estimado: Optional[str] = None
    ordem_embarque: int
    pessoa_nome: Optional[str] = None
    ponto_nome: Optional[str] = None

    class Config:
        from_attributes = True


class AlocacaoDiariaBase(BaseModel):
    """Base para alocação de diária."""
    veiculo_id: int
    rota_id: Optional[int] = None
    horario_saida: Optional[str] = None
    observacao: Optional[str] = None


class AlocacaoDiariaCreate(AlocacaoDiariaBase):
    """Schema para criação de alocação."""
    colaboradores: List[AlocacaoColaboradorBase] = []


class AlocacaoDiariaResponse(BaseModel):
    """Resposta de alocação de diária."""
    id: int
    diaria_id: int
    veiculo_id: int
    rota_id: Optional[int] = None
    horario_saida: Optional[str] = None
    observacao: Optional[str] = None
    veiculo_placa: Optional[str] = None
    veiculo_modelo: Optional[str] = None
    motorista: Optional[str] = None
    telefone_motorista: Optional[str] = None
    colaboradores: List[AlocacaoColaboradorResponse] = []

    class Config:
        from_attributes = True


class GerarAlocacaoRequest(BaseModel):
    """Request para gerar alocação automática."""
    horario_saida: str  # HH:MM


class GerarAlocacaoResponse(BaseModel):
    """Resposta da geração de alocação."""
    sucesso: bool
    mensagem: str
    alocacoes: List[AlocacaoDiariaResponse] = []
    veiculos_usados: int = 0
    colaboradores_alocados: int = 0
    colaboradores_sem_ponto: List[str] = []


# ========== Schema para visualização do colaborador ==========

class MinhaAlocacaoResponse(BaseModel):
    """O que o colaborador vê sobre sua alocação."""
    diaria_id: int
    diaria_titulo: str
    diaria_data: str
    diaria_local: Optional[str] = None
    veiculo_placa: str
    veiculo_modelo: str
    veiculo_cor: Optional[str] = None
    motorista: Optional[str] = None
    telefone_motorista: Optional[str] = None
    ponto_nome: Optional[str] = None
    ponto_endereco: Optional[str] = None
    horario_estimado: Optional[str] = None
    ordem_embarque: int = 0
