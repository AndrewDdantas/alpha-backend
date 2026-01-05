from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.rota import Rota, PontoParada
from app.repositories.rota_repository import RotaRepository, PontoParadaRepository
from app.schemas.rota import (
    RotaCreate, RotaUpdate, RotaList, RotaComPontos,
    PontoParadaCreate, PontoParadaUpdate,
)


class RotaService:
    """Serviço para regras de negócio de Rota."""

    def __init__(self, db: Session):
        self.repository = RotaRepository(db)
        self.ponto_repository = PontoParadaRepository(db)

    def get_rota(self, rota_id: int) -> Rota:
        """Busca rota por ID."""
        rota = self.repository.get_by_id(rota_id)
        if not rota:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rota não encontrada",
            )
        return rota

    def get_rota_com_pontos(self, rota_id: int) -> RotaComPontos:
        """Busca rota com seus pontos de parada."""
        rota = self.get_rota(rota_id)
        pontos = self.ponto_repository.get_by_rota(rota_id)
        return RotaComPontos(
            id=rota.id,
            nome=rota.nome,
            descricao=rota.descricao,
            ativo=rota.ativo,
            criado_em=rota.criado_em,
            atualizado_em=rota.atualizado_em,
            pontos_parada=pontos,
        )

    def list_rotas(self, skip: int = 0, limit: int = 100) -> RotaList:
        """Lista todas as rotas ativas."""
        rotas = self.repository.get_all(skip=skip, limit=limit)
        total = self.repository.count()
        return RotaList(total=total, rotas=rotas)

    def create_rota(self, rota_data: RotaCreate) -> Rota:
        """Cria uma nova rota."""
        return self.repository.create(rota_data)

    def update_rota(self, rota_id: int, rota_data: RotaUpdate) -> Rota:
        """Atualiza uma rota existente."""
        self.get_rota(rota_id)
        return self.repository.update(rota_id, rota_data)

    def delete_rota(self, rota_id: int) -> bool:
        """Remove uma rota."""
        self.get_rota(rota_id)
        return self.repository.delete(rota_id)


class PontoParadaService:
    """Serviço para regras de negócio de Ponto de Parada."""

    def __init__(self, db: Session):
        self.repository = PontoParadaRepository(db)
        self.rota_repository = RotaRepository(db)

    def get_ponto(self, ponto_id: int) -> PontoParada:
        """Busca ponto por ID."""
        ponto = self.repository.get_by_id(ponto_id)
        if not ponto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ponto de parada não encontrado",
            )
        return ponto

    def list_pontos_by_rota(self, rota_id: int) -> List[PontoParada]:
        """Lista pontos de uma rota."""
        # Verifica se rota existe
        rota = self.rota_repository.get_by_id(rota_id)
        if not rota:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rota não encontrada",
            )
        return self.repository.get_by_rota(rota_id)

    def create_ponto(self, ponto_data: PontoParadaCreate) -> PontoParada:
        """Cria um novo ponto de parada."""
        # Verifica se rota existe
        rota = self.rota_repository.get_by_id(ponto_data.rota_id)
        if not rota:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rota não encontrada",
            )
        return self.repository.create(ponto_data)

    def update_ponto(self, ponto_id: int, ponto_data: PontoParadaUpdate) -> PontoParada:
        """Atualiza um ponto de parada."""
        self.get_ponto(ponto_id)
        return self.repository.update(ponto_id, ponto_data)

    def delete_ponto(self, ponto_id: int) -> bool:
        """Remove um ponto de parada."""
        self.get_ponto(ponto_id)
        return self.repository.delete(ponto_id)
