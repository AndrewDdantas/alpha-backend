from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.perfil_repository import PerfilRepository
from app.schemas.perfil import (
    PerfilCreate,
    PerfilUpdate,
    PermissaoCreate,
    PermissaoUpdate,
)


class PerfilService:
    """Service para lógica de negócio de Perfis e Permissões."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = PerfilRepository(db)

    # ========== Serviços de Perfil ==========

    def get_perfil(self, perfil_id: int):
        """Retorna um perfil por ID."""
        perfil = self.repository.get_perfil(perfil_id)
        if not perfil:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil não encontrado",
            )
        return perfil

    def list_perfis(
        self,
        skip: int = 0,
        limit: int = 100,
        ativo: Optional[bool] = None,
        sistema: Optional[bool] = None,
    ):
        """Lista todos os perfis."""
        items, total = self.repository.list_perfis(
            skip=skip, limit=limit, ativo=ativo, sistema=sistema
        )
        return {"items": items, "total": total}

    def create_perfil(self, perfil_data: PerfilCreate):
        """Cria um novo perfil."""
        # Verifica se já existe perfil com o mesmo código
        existing = self.repository.get_perfil_by_codigo(perfil_data.codigo)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Já existe um perfil com o código '{perfil_data.codigo}'",
            )

        # Cria o perfil
        perfil = self.repository.create_perfil(
            nome=perfil_data.nome,
            codigo=perfil_data.codigo,
            descricao=perfil_data.descricao,
            ativo=perfil_data.ativo,
        )

        # Adiciona permissões se fornecidas
        if perfil_data.permissoes_ids:
            perfil = self.repository.substituir_permissoes_do_perfil(
                perfil.id, perfil_data.permissoes_ids
            )

        return perfil

    def update_perfil(self, perfil_id: int, perfil_data: PerfilUpdate):
        """Atualiza um perfil."""
        perfil = self.repository.get_perfil(perfil_id)
        if not perfil:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil não encontrado",
            )

        # Perfis de sistema não podem ser desativados
        if perfil.sistema and perfil_data.ativo is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Perfis de sistema não podem ser desativados",
            )

        # Atualiza campos básicos
        perfil = self.repository.update_perfil(
            perfil_id=perfil_id,
            nome=perfil_data.nome,
            descricao=perfil_data.descricao,
            ativo=perfil_data.ativo,
        )

        # Atualiza permissões se fornecidas
        if perfil_data.permissoes_ids is not None:
            perfil = self.repository.substituir_permissoes_do_perfil(
                perfil_id, perfil_data.permissoes_ids
            )

        return perfil

    def delete_perfil(self, perfil_id: int):
        """Remove um perfil."""
        perfil = self.repository.get_perfil(perfil_id)
        if not perfil:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil não encontrado",
            )

        if perfil.sistema:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Perfis de sistema não podem ser excluídos",
            )

        success = self.repository.delete_perfil(perfil_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao excluir perfil",
            )

        return {"message": "Perfil excluído com sucesso"}

    # ========== Serviços de Permissão ==========

    def get_permissao(self, permissao_id: int):
        """Retorna uma permissão por ID."""
        permissao = self.repository.get_permissao(permissao_id)
        if not permissao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permissão não encontrada",
            )
        return permissao

    def list_permissoes(
        self,
        skip: int = 0,
        limit: int = 100,
        ativo: Optional[bool] = None,
        recurso: Optional[str] = None,
    ):
        """Lista todas as permissões."""
        items, total = self.repository.list_permissoes(
            skip=skip, limit=limit, ativo=ativo, recurso=recurso
        )
        return {"items": items, "total": total}

    def create_permissao(self, permissao_data: PermissaoCreate):
        """Cria uma nova permissão."""
        # Verifica se já existe permissão com o mesmo código
        existing = self.repository.get_permissao_by_codigo(permissao_data.codigo)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Já existe uma permissão com o código '{permissao_data.codigo}'",
            )

        return self.repository.create_permissao(
            codigo=permissao_data.codigo,
            nome=permissao_data.nome,
            recurso=permissao_data.recurso,
            acao=permissao_data.acao,
            descricao=permissao_data.descricao,
            ativo=permissao_data.ativo,
        )

    def update_permissao(self, permissao_id: int, permissao_data: PermissaoUpdate):
        """Atualiza uma permissão."""
        permissao = self.repository.update_permissao(
            permissao_id=permissao_id,
            nome=permissao_data.nome,
            descricao=permissao_data.descricao,
            ativo=permissao_data.ativo,
        )
        if not permissao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permissão não encontrada",
            )
        return permissao

    def delete_permissao(self, permissao_id: int):
        """Remove uma permissão."""
        success = self.repository.delete_permissao(permissao_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permissão não encontrada",
            )
        return {"message": "Permissão excluída com sucesso"}

    # ========== Serviços de Atribuição ==========

    def atribuir_perfil_a_pessoa(
        self, pessoa_id: int, perfil_id: int, atribuido_por_id: Optional[int] = None
    ):
        """Atribui um perfil a uma pessoa."""
        success = self.repository.atribuir_perfil_a_pessoa(
            pessoa_id=pessoa_id,
            perfil_id=perfil_id,
            atribuido_por_id=atribuido_por_id,
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pessoa ou perfil não encontrado",
            )
        return {"message": "Perfil atribuído com sucesso"}

    def remover_perfil_de_pessoa(self, pessoa_id: int, perfil_id: int):
        """Remove um perfil de uma pessoa."""
        success = self.repository.remover_perfil_de_pessoa(pessoa_id, perfil_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pessoa ou perfil não encontrado",
            )
        return {"message": "Perfil removido com sucesso"}

    def get_perfis_da_pessoa(self, pessoa_id: int):
        """Retorna todos os perfis de uma pessoa."""
        perfis = self.repository.get_perfis_da_pessoa(pessoa_id)
        return perfis

    def get_permissoes_da_pessoa(self, pessoa_id: int):
        """Retorna todas as permissões de uma pessoa."""
        permissoes = self.repository.get_permissoes_da_pessoa(pessoa_id)
        return permissoes

    def verificar_permissao(self, pessoa_id: int, codigo_permissao: str) -> bool:
        """Verifica se uma pessoa tem uma permissão específica."""
        return self.repository.pessoa_tem_permissao(pessoa_id, codigo_permissao)
