from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.veiculo import Veiculo
from app.schemas.veiculo import VeiculoCreate, VeiculoUpdate


class VeiculoRepository:
    """Repositório para operações de Veículo no banco de dados."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100, apenas_ativos: bool = True) -> List[Veiculo]:
        """Retorna lista de veículos."""
        query = self.db.query(Veiculo)
        if apenas_ativos:
            query = query.filter(Veiculo.ativo == True)
        return query.offset(skip).limit(limit).all()

    def get_by_id(self, veiculo_id: int) -> Optional[Veiculo]:
        """Busca veículo por ID."""
        return self.db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()

    def get_by_placa(self, placa: str) -> Optional[Veiculo]:
        """Busca veículo por placa."""
        return self.db.query(Veiculo).filter(Veiculo.placa == placa).first()

    def create(self, veiculo_data: VeiculoCreate) -> Veiculo:
        """Cria um novo veículo."""
        db_veiculo = Veiculo(**veiculo_data.model_dump())
        self.db.add(db_veiculo)
        self.db.commit()
        self.db.refresh(db_veiculo)
        return db_veiculo

    def update(self, veiculo: Veiculo, veiculo_data: VeiculoUpdate) -> Veiculo:
        """Atualiza um veículo existente."""
        update_data = veiculo_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(veiculo, key, value)
        self.db.commit()
        self.db.refresh(veiculo)
        return veiculo

    def delete(self, veiculo: Veiculo) -> None:
        """Remove um veículo (soft delete)."""
        veiculo.ativo = False
        self.db.commit()

    def count(self, apenas_ativos: bool = True) -> int:
        """Conta total de veículos."""
        query = self.db.query(Veiculo)
        if apenas_ativos:
            query = query.filter(Veiculo.ativo == True)
        return query.count()

    def get_capacidade_total(self) -> int:
        """Retorna capacidade total de todos os veículos ativos."""
        from sqlalchemy import func
        result = self.db.query(func.sum(Veiculo.capacidade)).filter(Veiculo.ativo == True).scalar()
        return result or 0
