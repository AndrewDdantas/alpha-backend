from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.pessoa import Pessoa
from app.repositories.pessoa_repository import PessoaRepository
from app.schemas.pessoa import PessoaCreate, PessoaUpdate, PessoaList, PerfilUpdate


class PessoaService:
    """Serviço para regras de negócio de Pessoa."""

    def __init__(self, db: Session):
        self.repository = PessoaRepository(db)

    def get_pessoa(self, pessoa_id: int) -> Pessoa:
        """Busca pessoa por ID."""
        pessoa = self.repository.get_by_id(pessoa_id)
        if not pessoa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pessoa não encontrada",
            )
        return pessoa

    def list_pessoas(self, skip: int = 0, limit: int = 100) -> PessoaList:
        """Lista todas as pessoas."""
        pessoas = self.repository.get_all(skip=skip, limit=limit)
        total = self.repository.count()
        return PessoaList(total=total, pessoas=pessoas)

    def create_pessoa(self, pessoa_data: PessoaCreate) -> Pessoa:
        """Cria uma nova pessoa com validações."""
        # Verifica se email já existe
        if self.repository.get_by_email(pessoa_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado",
            )

        # Verifica se CPF já existe
        if self.repository.get_by_cpf(pessoa_data.cpf):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado",
            )

        return self.repository.create(pessoa_data)

    def update_pessoa(self, pessoa_id: int, pessoa_data: PessoaUpdate) -> Pessoa:
        """Atualiza uma pessoa existente."""
        # Verifica se pessoa existe
        self.get_pessoa(pessoa_id)

        # Verifica se novo email já está em uso
        if pessoa_data.email:
            existing = self.repository.get_by_email(pessoa_data.email)
            if existing and existing.id != pessoa_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email já está em uso",
                )

        updated = self.repository.update(pessoa_id, pessoa_data)
        return updated

    def update_perfil(self, pessoa_id: int, perfil_data: PerfilUpdate) -> Pessoa:
        """Atualiza o perfil do usuário (campos editáveis apenas)."""
        pessoa = self.get_pessoa(pessoa_id)

        # Atualiza apenas os campos permitidos
        update_data = perfil_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(pessoa, field, value)

        self.repository.db.commit()
        self.repository.db.refresh(pessoa)
        return pessoa

    def delete_pessoa(self, pessoa_id: int) -> bool:
        """Remove uma pessoa."""
        self.get_pessoa(pessoa_id)  # Verifica se existe
        return self.repository.delete(pessoa_id)

