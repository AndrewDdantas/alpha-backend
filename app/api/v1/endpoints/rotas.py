from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.permissions import require_admin
from app.models.pessoa import Pessoa
from app.schemas.rota import (
    RotaCreate, RotaUpdate, RotaResponse, RotaList, RotaComPontos,
    PontoParadaCreate, PontoParadaUpdate, PontoParadaResponse,
)
from app.services.rota_service import RotaService, PontoParadaService

router = APIRouter()


# ========== Rotas de Fretados ==========

@router.get("/", response_model=RotaList)
def list_rotas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Lista todas as rotas de fretados ativas."""
    service = RotaService(db)
    return service.list_rotas(skip=skip, limit=limit)


@router.get("/{rota_id}", response_model=RotaComPontos)
def get_rota(
    rota_id: int,
    db: Session = Depends(get_db),
):
    """Busca uma rota com seus pontos de parada."""
    service = RotaService(db)
    return service.get_rota_com_pontos(rota_id)


@router.post("/", response_model=RotaResponse, status_code=status.HTTP_201_CREATED)
def create_rota(
    rota_data: RotaCreate,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Cria uma nova rota de fretado (apenas admin)."""
    service = RotaService(db)
    return service.create_rota(rota_data)


@router.put("/{rota_id}", response_model=RotaResponse)
def update_rota(
    rota_id: int,
    rota_data: RotaUpdate,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Atualiza uma rota de fretado (apenas admin)."""
    service = RotaService(db)
    return service.update_rota(rota_id, rota_data)


@router.delete("/{rota_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rota(
    rota_id: int,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Remove uma rota de fretado (apenas admin)."""
    service = RotaService(db)
    service.delete_rota(rota_id)
    return None


# ========== Pontos de Parada ==========

@router.get("/{rota_id}/pontos", response_model=List[PontoParadaResponse])
def list_pontos(
    rota_id: int,
    db: Session = Depends(get_db),
):
    """Lista pontos de parada de uma rota."""
    service = PontoParadaService(db)
    return service.list_pontos_by_rota(rota_id)


@router.post("/{rota_id}/pontos", response_model=PontoParadaResponse, status_code=status.HTTP_201_CREATED)
def create_ponto(
    rota_id: int,
    ponto_data: PontoParadaCreate,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Cria um novo ponto de parada (apenas admin)."""
    # Garante que o rota_id do path seja usado
    ponto_data.rota_id = rota_id
    service = PontoParadaService(db)
    return service.create_ponto(ponto_data)


@router.put("/pontos/{ponto_id}", response_model=PontoParadaResponse)
def update_ponto(
    ponto_id: int,
    ponto_data: PontoParadaUpdate,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Atualiza um ponto de parada (apenas admin)."""
    service = PontoParadaService(db)
    return service.update_ponto(ponto_id, ponto_data)


@router.delete("/pontos/{ponto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ponto(
    ponto_id: int,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Remove um ponto de parada (apenas admin)."""
    service = PontoParadaService(db)
    service.delete_ponto(ponto_id)
    return None
