"""Endpoints para busca de pontos de ônibus via OpenStreetMap."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.deps import get_db
from app.core.permissions import require_admin
from app.models.pessoa import Pessoa
from app.services.overpass_service import get_overpass_service

router = APIRouter()


class PontoOnibusResponse(BaseModel):
    """Schema de resposta para ponto de ônibus."""
    id: Optional[int] = None
    osm_id: str
    nome: Optional[str] = None
    latitude: float
    longitude: float
    cidade: str


class BuscaPontosResponse(BaseModel):
    """Resposta da busca de pontos."""
    cidade: str
    total: int
    pontos: List[PontoOnibusResponse]
    from_cache: bool


@router.get("/{cidade}", response_model=BuscaPontosResponse)
def buscar_pontos_onibus(
    cidade: str,
    force_refresh: bool = Query(False, description="Forçar nova busca ignorando cache"),
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """
    Busca pontos de ônibus de uma cidade via OpenStreetMap.
    
    Os resultados são cacheados no banco de dados para evitar
    consultas repetidas à API do OpenStreetMap.
    
    Args:
        cidade: Nome da cidade (ex: "Jundiaí", "São Paulo")
        force_refresh: Se True, ignora cache e faz nova consulta
    """
    service = get_overpass_service(db)
    
    # Verifica se tem cache antes de buscar
    from app.models.ponto_onibus import PontoOnibus
    cache_count = db.query(PontoOnibus).filter(
        PontoOnibus.cidade == cidade.strip().title()
    ).count()
    
    from_cache = cache_count > 0 and not force_refresh
    
    pontos = service.buscar_pontos_cidade(cidade, force_refresh=force_refresh)
    
    return BuscaPontosResponse(
        cidade=cidade.strip().title(),
        total=len(pontos),
        pontos=[PontoOnibusResponse(**p) for p in pontos],
        from_cache=from_cache,
    )


@router.get("/", response_model=List[str])
def listar_cidades_cacheadas(
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Lista todas as cidades que já têm pontos cacheados."""
    from app.models.ponto_onibus import PontoOnibus
    from sqlalchemy import distinct
    
    cidades = db.query(distinct(PontoOnibus.cidade)).all()
    return [c[0] for c in cidades]
