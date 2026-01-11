"""Repository para gerenciar registros de presença."""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.presenca import RegistroPresenca


class PresencaRepository:
    """Repository para operações com registros de presença."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, presenca_id: int) -> Optional[RegistroPresenca]:
        """Busca um registro de presença pelo ID."""
        return self.db.query(RegistroPresenca).filter(
            RegistroPresenca.id == presenca_id
        ).first()

    def get_by_inscricao(self, inscricao_id: int) -> Optional[RegistroPresenca]:
        """Busca registro de presença por ID da inscrição."""
        return self.db.query(RegistroPresenca).filter(
            RegistroPresenca.inscricao_id == inscricao_id
        ).first()

    def get_by_diaria(self, diaria_id: int) -> List[RegistroPresenca]:
        """Lista todos os registros de presença de uma diária."""
        from app.models.diaria import Inscricao
        return self.db.query(RegistroPresenca).join(
            Inscricao, RegistroPresenca.inscricao_id == Inscricao.id
        ).filter(
            Inscricao.diaria_id == diaria_id
        ).all()

    def create(self, presenca_data: dict) -> RegistroPresenca:
        """Cria um novo registro de presença."""
        presenca = RegistroPresenca(**presenca_data)
        self.db.add(presenca)
        self.db.commit()
        self.db.refresh(presenca)
        return presenca

    def delete(self, presenca_id: int) -> bool:
        """Remove um registro de presença."""
        presenca = self.get_by_id(presenca_id)
        if presenca:
            self.db.delete(presenca)
            self.db.commit()
            return True
        return False
