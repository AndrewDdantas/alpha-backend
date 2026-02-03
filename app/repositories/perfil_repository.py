from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.models.perfil import Perfil, Permissao, pessoa_perfil
from app.models.pessoa import Pessoa


class PerfilRepository:
    """Repository para operações de Perfil."""

    def __init__(self, db: Session):
        self.db = db

    # ========== CRUD de Perfil ==========

    def get_perfil(self, perfil_id: int) -> Optional[Perfil]:
        """Retorna um perfil por ID com suas permissões."""
        return (
            self.db.query(Perfil)
            .options(joinedload(Perfil.permissoes))
            .filter(Perfil.id == perfil_id)
            .first()
        )

    def get_perfil_by_codigo(self, codigo: str) -> Optional[Perfil]:
        """Retorna um perfil por código."""
        return (
            self.db.query(Perfil)
            .options(joinedload(Perfil.permissoes))
            .filter(Perfil.codigo == codigo)
            .first()
        )

    def list_perfis(
        self,
        skip: int = 0,
        limit: int = 100,
        ativo: Optional[bool] = None,
        sistema: Optional[bool] = None,
    ) -> tuple[List[Perfil], int]:
        """Lista todos os perfis com filtros."""
        query = self.db.query(Perfil).options(joinedload(Perfil.permissoes))

        if ativo is not None:
            query = query.filter(Perfil.ativo == ativo)
        if sistema is not None:
            query = query.filter(Perfil.sistema == sistema)

        total = query.count()
        items = query.order_by(Perfil.nome).offset(skip).limit(limit).all()

        return items, total

    def create_perfil(
        self,
        nome: str,
        codigo: str,
        descricao: Optional[str] = None,
        sistema: bool = False,
        ativo: bool = True,
    ) -> Perfil:
        """Cria um novo perfil."""
        perfil = Perfil(
            nome=nome,
            codigo=codigo,
            descricao=descricao,
            sistema=sistema,
            ativo=ativo,
        )
        self.db.add(perfil)
        self.db.commit()
        self.db.refresh(perfil)
        return perfil

    def update_perfil(
        self,
        perfil_id: int,
        nome: Optional[str] = None,
        descricao: Optional[str] = None,
        ativo: Optional[bool] = None,
    ) -> Optional[Perfil]:
        """Atualiza um perfil."""
        perfil = self.get_perfil(perfil_id)
        if not perfil:
            return None

        if nome is not None:
            perfil.nome = nome
        if descricao is not None:
            perfil.descricao = descricao
        if ativo is not None:
            perfil.ativo = ativo

        self.db.commit()
        self.db.refresh(perfil)
        return perfil

    def delete_perfil(self, perfil_id: int) -> bool:
        """Remove um perfil (apenas se não for de sistema)."""
        perfil = self.get_perfil(perfil_id)
        if not perfil or perfil.sistema:
            return False

        self.db.delete(perfil)
        self.db.commit()
        return True

    # ========== CRUD de Permissão ==========

    def get_permissao(self, permissao_id: int) -> Optional[Permissao]:
        """Retorna uma permissão por ID."""
        return self.db.query(Permissao).filter(Permissao.id == permissao_id).first()

    def get_permissao_by_codigo(self, codigo: str) -> Optional[Permissao]:
        """Retorna uma permissão por código."""
        return self.db.query(Permissao).filter(Permissao.codigo == codigo).first()

    def list_permissoes(
        self,
        skip: int = 0,
        limit: int = 100,
        ativo: Optional[bool] = None,
        recurso: Optional[str] = None,
    ) -> tuple[List[Permissao], int]:
        """Lista todas as permissões com filtros."""
        query = self.db.query(Permissao)

        if ativo is not None:
            query = query.filter(Permissao.ativo == ativo)
        if recurso:
            query = query.filter(Permissao.recurso == recurso)

        total = query.count()
        items = query.order_by(Permissao.recurso, Permissao.acao).offset(skip).limit(limit).all()

        return items, total

    def create_permissao(
        self,
        codigo: str,
        nome: str,
        recurso: str,
        acao: str,
        descricao: Optional[str] = None,
        ativo: bool = True,
    ) -> Permissao:
        """Cria uma nova permissão."""
        permissao = Permissao(
            codigo=codigo,
            nome=nome,
            descricao=descricao,
            recurso=recurso,
            acao=acao,
            ativo=ativo,
        )
        self.db.add(permissao)
        self.db.commit()
        self.db.refresh(permissao)
        return permissao

    def update_permissao(
        self,
        permissao_id: int,
        nome: Optional[str] = None,
        descricao: Optional[str] = None,
        ativo: Optional[bool] = None,
    ) -> Optional[Permissao]:
        """Atualiza uma permissão."""
        permissao = self.get_permissao(permissao_id)
        if not permissao:
            return None

        if nome is not None:
            permissao.nome = nome
        if descricao is not None:
            permissao.descricao = descricao
        if ativo is not None:
            permissao.ativo = ativo

        self.db.commit()
        self.db.refresh(permissao)
        return permissao

    def delete_permissao(self, permissao_id: int) -> bool:
        """Remove uma permissão."""
        permissao = self.get_permissao(permissao_id)
        if not permissao:
            return False

        self.db.delete(permissao)
        self.db.commit()
        return True

    # ========== Gestão de Permissões do Perfil ==========

    def adicionar_permissoes_ao_perfil(
        self, perfil_id: int, permissoes_ids: List[int]
    ) -> Optional[Perfil]:
        """Adiciona permissões a um perfil."""
        perfil = self.get_perfil(perfil_id)
        if not perfil:
            return None

        permissoes = self.db.query(Permissao).filter(Permissao.id.in_(permissoes_ids)).all()
        perfil.permissoes.extend(permissoes)

        self.db.commit()
        self.db.refresh(perfil)
        return perfil

    def remover_permissoes_do_perfil(
        self, perfil_id: int, permissoes_ids: List[int]
    ) -> Optional[Perfil]:
        """Remove permissões de um perfil."""
        perfil = self.get_perfil(perfil_id)
        if not perfil:
            return None

        permissoes_remover = [p for p in perfil.permissoes if p.id in permissoes_ids]
        for perm in permissoes_remover:
            perfil.permissoes.remove(perm)

        self.db.commit()
        self.db.refresh(perfil)
        return perfil

    def substituir_permissoes_do_perfil(
        self, perfil_id: int, permissoes_ids: List[int]
    ) -> Optional[Perfil]:
        """Substitui todas as permissões de um perfil."""
        perfil = self.get_perfil(perfil_id)
        if not perfil:
            return None

        permissoes = self.db.query(Permissao).filter(Permissao.id.in_(permissoes_ids)).all()
        perfil.permissoes = permissoes

        self.db.commit()
        self.db.refresh(perfil)
        return perfil

    # ========== Gestão de Perfis do Usuário ==========

    def atribuir_perfil_a_pessoa(
        self, pessoa_id: int, perfil_id: int, atribuido_por_id: Optional[int] = None
    ) -> bool:
        """Atribui um perfil a uma pessoa."""
        pessoa = self.db.query(Pessoa).filter(Pessoa.id == pessoa_id).first()
        perfil = self.get_perfil(perfil_id)

        if not pessoa or not perfil:
            return False

        # Verifica se já tem o perfil
        if perfil in pessoa.perfis:
            return True

        pessoa.perfis.append(perfil)
        self.db.commit()
        return True

    def remover_perfil_de_pessoa(self, pessoa_id: int, perfil_id: int) -> bool:
        """Remove um perfil de uma pessoa."""
        pessoa = (
            self.db.query(Pessoa)
            .options(joinedload(Pessoa.perfis))
            .filter(Pessoa.id == pessoa_id)
            .first()
        )
        perfil = self.get_perfil(perfil_id)

        if not pessoa or not perfil:
            return False

        if perfil in pessoa.perfis:
            pessoa.perfis.remove(perfil)
            self.db.commit()

        return True

    def get_perfis_da_pessoa(self, pessoa_id: int) -> List[Perfil]:
        """Retorna todos os perfis de uma pessoa."""
        pessoa = (
            self.db.query(Pessoa)
            .options(joinedload(Pessoa.perfis))
            .filter(Pessoa.id == pessoa_id)
            .first()
        )
        if not pessoa:
            return []

        return pessoa.perfis

    def get_permissoes_da_pessoa(self, pessoa_id: int) -> List[Permissao]:
        """Retorna todas as permissões de uma pessoa (através dos perfis)."""
        pessoa = (
            self.db.query(Pessoa)
            .options(joinedload(Pessoa.perfis).joinedload(Perfil.permissoes))
            .filter(Pessoa.id == pessoa_id)
            .first()
        )
        if not pessoa:
            return []

        # Coleta todas as permissões de todos os perfis (sem duplicatas)
        permissoes = set()
        for perfil in pessoa.perfis:
            if perfil.ativo:
                permissoes.update([p for p in perfil.permissoes if p.ativo])

        return list(permissoes)

    def pessoa_tem_permissao(self, pessoa_id: int, codigo_permissao: str) -> bool:
        """Verifica se uma pessoa tem uma permissão específica."""
        permissoes = self.get_permissoes_da_pessoa(pessoa_id)
        return any(p.codigo == codigo_permissao for p in permissoes)
