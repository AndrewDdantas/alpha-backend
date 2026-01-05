from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.empresa import Empresa
from app.repositories.empresa_repository import EmpresaRepository
from app.schemas.empresa import EmpresaCreate, EmpresaUpdate, EmpresaList


class EmpresaService:
    """Serviço para regras de negócio de Empresa."""

    def __init__(self, db: Session):
        self.repository = EmpresaRepository(db)

    def get_empresa(self, empresa_id: int) -> Empresa:
        """Busca empresa por ID."""
        empresa = self.repository.get_by_id(empresa_id)
        if not empresa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empresa não encontrada",
            )
        return empresa

    def list_empresas(self, skip: int = 0, limit: int = 100) -> EmpresaList:
        """Lista todas as empresas ativas."""
        empresas = self.repository.get_all(skip=skip, limit=limit)
        total = self.repository.count()
        return EmpresaList(total=total, empresas=empresas)

    def create_empresa(self, empresa_data: EmpresaCreate) -> Empresa:
        """Cria uma nova empresa."""
        # Verifica se CNPJ já existe
        if self.repository.get_by_cnpj(empresa_data.cnpj):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CNPJ já cadastrado",
            )
        return self.repository.create(empresa_data)

    def update_empresa(self, empresa_id: int, empresa_data: EmpresaUpdate) -> Empresa:
        """Atualiza uma empresa existente."""
        self.get_empresa(empresa_id)
        return self.repository.update(empresa_id, empresa_data)

    def delete_empresa(self, empresa_id: int) -> bool:
        """Remove uma empresa."""
        self.get_empresa(empresa_id)
        return self.repository.delete(empresa_id)
