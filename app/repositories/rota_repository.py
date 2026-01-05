from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.rota import Rota, PontoParada
from app.schemas.rota import RotaCreate, RotaUpdate, PontoParadaCreate, PontoParadaUpdate


class RotaRepository:
    """Repositório para operações CRUD de Rota."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, rota_id: int) -> Optional[Rota]:
        """Busca rota por ID."""
        return self.db.query(Rota).filter(Rota.id == rota_id).first()

    def get_all(self, skip: int = 0, limit: int = 100, apenas_ativas: bool = True) -> List[Rota]:
        """Lista todas as rotas com paginação."""
        query = self.db.query(Rota)
        if apenas_ativas:
            query = query.filter(Rota.ativo == True)
        return query.offset(skip).limit(limit).all()

    def count(self, apenas_ativas: bool = True) -> int:
        """Conta total de rotas."""
        query = self.db.query(Rota)
        if apenas_ativas:
            query = query.filter(Rota.ativo == True)
        return query.count()

    def create(self, rota_data: RotaCreate) -> Rota:
        """Cria uma nova rota."""
        db_rota = Rota(
            nome=rota_data.nome,
            descricao=rota_data.descricao,
        )
        self.db.add(db_rota)
        self.db.commit()
        self.db.refresh(db_rota)
        return db_rota

    def update(self, rota_id: int, rota_data: RotaUpdate) -> Optional[Rota]:
        """Atualiza uma rota existente."""
        db_rota = self.get_by_id(rota_id)
        if not db_rota:
            return None

        update_data = rota_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_rota, field, value)

        self.db.commit()
        self.db.refresh(db_rota)
        return db_rota

    def delete(self, rota_id: int) -> bool:
        """Remove uma rota."""
        db_rota = self.get_by_id(rota_id)
        if not db_rota:
            return False

        self.db.delete(db_rota)
        self.db.commit()
        return True


class PontoParadaRepository:
    """Repositório para operações CRUD de Ponto de Parada."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, ponto_id: int) -> Optional[PontoParada]:
        """Busca ponto por ID."""
        return self.db.query(PontoParada).filter(PontoParada.id == ponto_id).first()

    def get_by_rota(self, rota_id: int, apenas_ativos: bool = True) -> List[PontoParada]:
        """Lista pontos de parada de uma rota."""
        query = self.db.query(PontoParada).filter(PontoParada.rota_id == rota_id)
        if apenas_ativos:
            query = query.filter(PontoParada.ativo == True)
        return query.order_by(PontoParada.ordem).all()

    def create(self, ponto_data: PontoParadaCreate) -> PontoParada:
        """Cria um novo ponto de parada."""
        db_ponto = PontoParada(
            nome=ponto_data.nome,
            endereco=ponto_data.endereco,
            referencia=ponto_data.referencia,
            latitude=ponto_data.latitude,
            longitude=ponto_data.longitude,
            horario=ponto_data.horario,
            ordem=ponto_data.ordem,
            rota_id=ponto_data.rota_id,
        )
        self.db.add(db_ponto)
        self.db.commit()
        self.db.refresh(db_ponto)
        return db_ponto

    def update(self, ponto_id: int, ponto_data: PontoParadaUpdate) -> Optional[PontoParada]:
        """Atualiza um ponto de parada."""
        db_ponto = self.get_by_id(ponto_id)
        if not db_ponto:
            return None

        update_data = ponto_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_ponto, field, value)

        self.db.commit()
        self.db.refresh(db_ponto)
        return db_ponto

    def delete(self, ponto_id: int) -> bool:
        """Remove um ponto de parada."""
        db_ponto = self.get_by_id(ponto_id)
        if not db_ponto:
            return False

        self.db.delete(db_ponto)
        self.db.commit()
        return True
