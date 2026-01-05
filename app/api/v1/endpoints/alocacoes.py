from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.permissions import require_admin, require_authenticated
from app.models.pessoa import Pessoa
from app.schemas.alocacao import (
    GerarAlocacaoRequest, GerarAlocacaoResponse,
    AlocacaoDiariaResponse, MinhaAlocacaoResponse,
)
from app.services.alocacao_service import AlocacaoService

router = APIRouter()


@router.post(
    "/diarias/{diaria_id}/gerar-alocacao",
    response_model=GerarAlocacaoResponse,
)
def gerar_alocacao(
    diaria_id: int,
    request: GerarAlocacaoRequest,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """
    Gera alocação automática de veículos para uma diária.
    Distribui colaboradores inscritos em veículos disponíveis.
    """
    service = AlocacaoService(db)
    return service.gerar_alocacao_automatica(diaria_id, request.horario_saida)


@router.get(
    "/diarias/{diaria_id}/alocacao",
    response_model=List[AlocacaoDiariaResponse],
)
def get_alocacao(
    diaria_id: int,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Retorna alocação de veículos de uma diária (admin)."""
    service = AlocacaoService(db)
    return service.get_alocacoes_diaria(diaria_id)


@router.get(
    "/minhas-alocacoes",
    response_model=List[MinhaAlocacaoResponse],
)
def minhas_alocacoes(
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_authenticated()),
):
    """
    Retorna as alocações do colaborador logado.
    Mostra veículo, motorista e horário estimado de passagem.
    """
    service = AlocacaoService(db)
    return service.get_minhas_alocacoes(current_user.id)
