from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.diaria import Diaria, Inscricao
from app.models.enums import StatusDiaria, StatusInscricao
from app.schemas.diaria import DiariaCreate, DiariaUpdate, InscricaoCreate, InscricaoUpdate


class DiariaRepository:
    """Repositório para operações CRUD de Diária."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, diaria_id: int) -> Optional[Diaria]:
        """Busca diária por ID."""
        return self.db.query(Diaria).filter(Diaria.id == diaria_id).first()

    def get_by_id_with_empresa(self, diaria_id: int) -> Optional[Diaria]:
        """Busca diária por ID com empresa."""
        return (
            self.db.query(Diaria)
            .options(joinedload(Diaria.empresa))
            .filter(Diaria.id == diaria_id)
            .first()
        )

    def get_by_id_with_inscricoes(self, diaria_id: int) -> Optional[Diaria]:
        """Busca diária com inscrições e pessoas."""
        return (
            self.db.query(Diaria)
            .options(
                joinedload(Diaria.empresa),
                joinedload(Diaria.inscricoes).joinedload(Inscricao.pessoa)
            )
            .filter(Diaria.id == diaria_id)
            .first()
        )

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[StatusDiaria] = None,
        empresa_id: Optional[int] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
    ) -> List[Diaria]:
        """Lista diárias com filtros."""
        query = self.db.query(Diaria).options(joinedload(Diaria.empresa))

        if status:
            query = query.filter(Diaria.status == status)
        if empresa_id:
            query = query.filter(Diaria.empresa_id == empresa_id)
        if data_inicio:
            query = query.filter(Diaria.data >= data_inicio)
        if data_fim:
            query = query.filter(Diaria.data <= data_fim)

        return query.order_by(Diaria.data.desc()).offset(skip).limit(limit).all()

    def get_disponiveis(self, skip: int = 0, limit: int = 100) -> List[Diaria]:
        """Lista diárias abertas para inscrição."""
        return (
            self.db.query(Diaria)
            .options(joinedload(Diaria.empresa))
            .filter(Diaria.status == StatusDiaria.ABERTA)
            .filter(Diaria.data >= date.today())
            .order_by(Diaria.data)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count(self, status: Optional[StatusDiaria] = None) -> int:
        """Conta total de diárias."""
        query = self.db.query(Diaria)
        if status:
            query = query.filter(Diaria.status == status)
        return query.count()

    def create(self, diaria_data: DiariaCreate) -> Diaria:
        """Cria uma nova diária."""
        db_diaria = Diaria(
            titulo=diaria_data.titulo,
            descricao=diaria_data.descricao,
            data=diaria_data.data,
            horario_inicio=diaria_data.horario_inicio,
            horario_fim=diaria_data.horario_fim,
            vagas=diaria_data.vagas,
            valor=diaria_data.valor,
            local=diaria_data.local,
            observacoes=diaria_data.observacoes,
            empresa_id=diaria_data.empresa_id,
        )
        self.db.add(db_diaria)
        self.db.commit()
        self.db.refresh(db_diaria)
        return db_diaria

    def update(self, diaria_id: int, diaria_data: DiariaUpdate) -> Optional[Diaria]:
        """Atualiza uma diária."""
        db_diaria = self.get_by_id(diaria_id)
        if not db_diaria:
            return None

        update_data = diaria_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_diaria, field, value)

        self.db.commit()
        self.db.refresh(db_diaria)
        return db_diaria

    def delete(self, diaria_id: int) -> bool:
        """Remove uma diária."""
        db_diaria = self.get_by_id(diaria_id)
        if not db_diaria:
            return False

        self.db.delete(db_diaria)
        self.db.commit()
        return True


class InscricaoRepository:
    """Repositório para operações de Inscrição."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, inscricao_id: int) -> Optional[Inscricao]:
        """Busca inscrição por ID."""
        return self.db.query(Inscricao).filter(Inscricao.id == inscricao_id).first()

    def get_by_pessoa_e_diaria(self, pessoa_id: int, diaria_id: int) -> Optional[Inscricao]:
        """Busca inscrição de uma pessoa em uma diária específica."""
        return (
            self.db.query(Inscricao)
            .filter(Inscricao.pessoa_id == pessoa_id)
            .filter(Inscricao.diaria_id == diaria_id)
            .first()
        )

    def get_by_pessoa(self, pessoa_id: int, status: Optional[StatusInscricao] = None) -> List[Inscricao]:
        """Lista inscrições de uma pessoa."""
        query = (
            self.db.query(Inscricao)
            .options(
                joinedload(Inscricao.diaria).joinedload(Diaria.empresa)
            )
            .filter(Inscricao.pessoa_id == pessoa_id)
        )
        if status:
            query = query.filter(Inscricao.status == status)
        return query.order_by(Inscricao.criado_em.desc()).all()

    def get_inscricoes_ativas_pessoa(self, pessoa_id: int) -> List[Inscricao]:
        """Lista inscrições ativas (pendentes ou confirmadas) de uma pessoa com dados da diária."""
        from datetime import date as dt_date
        return (
            self.db.query(Inscricao)
            .options(joinedload(Inscricao.diaria))
            .filter(Inscricao.pessoa_id == pessoa_id)
            .filter(Inscricao.status.in_([StatusInscricao.PENDENTE, StatusInscricao.CONFIRMADA]))
            .join(Diaria)
            .filter(Diaria.data >= dt_date.today())
            .all()
        )

    def get_by_diaria(self, diaria_id: int) -> List[Inscricao]:
        """Lista inscrições de uma diária."""
        return (
            self.db.query(Inscricao)
            .options(joinedload(Inscricao.pessoa))
            .filter(Inscricao.diaria_id == diaria_id)
            .all()
        )

    def create(self, pessoa_id: int, inscricao_data: InscricaoCreate) -> Inscricao:
        """Cria uma nova inscrição."""
        db_inscricao = Inscricao(
            pessoa_id=pessoa_id,
            diaria_id=inscricao_data.diaria_id,
            observacao=inscricao_data.observacao,
        )
        self.db.add(db_inscricao)
        self.db.commit()
        self.db.refresh(db_inscricao)
        return db_inscricao

    def update(self, inscricao_id: int, inscricao_data: InscricaoUpdate) -> Optional[Inscricao]:
        """Atualiza uma inscrição."""
        db_inscricao = self.get_by_id(inscricao_id)
        if not db_inscricao:
            return None

        update_data = inscricao_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_inscricao, field, value)

        self.db.commit()
        self.db.refresh(db_inscricao)
        return db_inscricao

    def update_status(self, inscricao_id: int, status: StatusInscricao) -> Optional[Inscricao]:
        """Atualiza apenas o status de uma inscrição."""
        db_inscricao = self.get_by_id(inscricao_id)
        if not db_inscricao:
            return None

        db_inscricao.status = status
        self.db.commit()
        self.db.refresh(db_inscricao)
        return db_inscricao

    def delete(self, inscricao_id: int) -> bool:
        """Remove uma inscrição."""
        db_inscricao = self.get_by_id(inscricao_id)
        if not db_inscricao:
            return False

        self.db.delete(db_inscricao)
        self.db.commit()
        return True
