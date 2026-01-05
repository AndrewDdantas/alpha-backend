from datetime import date
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.diaria import Diaria, Inscricao
from app.models.enums import StatusDiaria, StatusInscricao
from app.repositories.diaria_repository import DiariaRepository, InscricaoRepository
from app.repositories.empresa_repository import EmpresaRepository
from app.schemas.diaria import (
    DiariaCreate, DiariaUpdate, DiariaList, DiariaComInscricoes,
    InscricaoCreate, InscricaoUpdate, MinhaInscricao,
)


class DiariaService:
    """Serviço para regras de negócio de Diária."""

    def __init__(self, db: Session):
        self.repository = DiariaRepository(db)
        self.empresa_repository = EmpresaRepository(db)

    def get_diaria(self, diaria_id: int) -> Diaria:
        """Busca diária por ID."""
        diaria = self.repository.get_by_id_with_empresa(diaria_id)
        if not diaria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diária não encontrada",
            )
        return diaria

    def get_diaria_com_inscricoes(self, diaria_id: int) -> DiariaComInscricoes:
        """Busca diária com lista de inscrições (para admin)."""
        diaria = self.repository.get_by_id_with_inscricoes(diaria_id)
        if not diaria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diária não encontrada",
            )
        return diaria

    def list_diarias(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[StatusDiaria] = None,
        empresa_id: Optional[int] = None,
    ) -> DiariaList:
        """Lista diárias com filtros (para admin)."""
        diarias = self.repository.get_all(
            skip=skip, limit=limit, status=status, empresa_id=empresa_id
        )
        total = self.repository.count(status=status)
        return DiariaList(total=total, diarias=diarias)

    def list_disponiveis(self, skip: int = 0, limit: int = 100) -> DiariaList:
        """Lista diárias disponíveis para inscrição (para colaboradores)."""
        diarias = self.repository.get_disponiveis(skip=skip, limit=limit)
        total = len(diarias)
        return DiariaList(total=total, diarias=diarias)

    def create_diaria(self, diaria_data: DiariaCreate) -> Diaria:
        """Cria uma nova diária."""
        # Verifica se empresa existe
        empresa = self.empresa_repository.get_by_id(diaria_data.empresa_id)
        if not empresa:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empresa não encontrada",
            )

        # Verifica se data não é passada
        if diaria_data.data < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data da diária não pode ser no passado",
            )

        return self.repository.create(diaria_data)

    def update_diaria(self, diaria_id: int, diaria_data: DiariaUpdate) -> Diaria:
        """Atualiza uma diária existente."""
        self.get_diaria(diaria_id)
        return self.repository.update(diaria_id, diaria_data)

    def delete_diaria(self, diaria_id: int) -> bool:
        """Remove uma diária."""
        self.get_diaria(diaria_id)
        return self.repository.delete(diaria_id)


class InscricaoService:
    """Serviço para regras de negócio de Inscrição."""

    def __init__(self, db: Session):
        self.repository = InscricaoRepository(db)
        self.diaria_repository = DiariaRepository(db)

    def get_inscricao(self, inscricao_id: int) -> Inscricao:
        """Busca inscrição por ID."""
        inscricao = self.repository.get_by_id(inscricao_id)
        if not inscricao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inscrição não encontrada",
            )
        return inscricao

    def minhas_inscricoes(self, pessoa_id: int) -> List[MinhaInscricao]:
        """Lista inscrições do colaborador."""
        inscricoes = self.repository.get_by_pessoa(pessoa_id)
        return inscricoes

    def inscrever(self, pessoa_id: int, inscricao_data: InscricaoCreate) -> Inscricao:
        """Inscreve colaborador em uma diária."""
        from datetime import datetime, timedelta
        from app.repositories.pessoa_repository import PessoaRepository

        # Verifica se pessoa está bloqueada
        pessoa_repo = PessoaRepository(self.repository.db)
        pessoa = pessoa_repo.get_by_id(pessoa_id)
        
        if pessoa and pessoa.bloqueado and pessoa.bloqueado_ate:
            if pessoa.bloqueado_ate >= date.today():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Você está bloqueado até {pessoa.bloqueado_ate.strftime('%d/%m/%Y')}. Motivo: {pessoa.motivo_bloqueio or 'Falta em diária anterior'}",
                )

        diaria = self.diaria_repository.get_by_id_with_inscricoes(inscricao_data.diaria_id)

        if not diaria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diária não encontrada",
            )

        # Verifica se diária está aberta
        if diaria.status != StatusDiaria.ABERTA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Esta diária não está aberta para inscrições",
            )

        # Verifica se data não passou
        if diaria.data < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Esta diária já passou",
            )

        # Verifica se já está inscrito nesta mesma diária
        inscricao_existente = self.repository.get_by_pessoa_e_diaria(pessoa_id, inscricao_data.diaria_id)
        if inscricao_existente:
            if inscricao_existente.status in [StatusInscricao.PENDENTE, StatusInscricao.CONFIRMADA]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Você já está inscrito nesta diária",
                )
            # Se estava cancelada/rejeitada, pode tentar novamente
            self.repository.delete(inscricao_existente.id)

        # ========== NOVA VALIDAÇÃO: Intervalo mínimo de 11 horas ==========
        # Verifica se há conflito com outras diárias ativas do colaborador
        inscricoes_ativas = self.repository.get_inscricoes_ativas_pessoa(pessoa_id)

        # Monta datetime da diária atual
        diaria_inicio = datetime.combine(
            diaria.data,
            diaria.horario_inicio if diaria.horario_inicio else datetime.min.time()
        )
        diaria_fim = datetime.combine(
            diaria.data,
            diaria.horario_fim if diaria.horario_fim else datetime.max.time()
        )

        for inscricao in inscricoes_ativas:
            outra_diaria = inscricao.diaria

            # Monta datetime da outra diária
            outra_inicio = datetime.combine(
                outra_diaria.data,
                outra_diaria.horario_inicio if outra_diaria.horario_inicio else datetime.min.time()
            )
            outra_fim = datetime.combine(
                outra_diaria.data,
                outra_diaria.horario_fim if outra_diaria.horario_fim else datetime.max.time()
            )

            # Calcula intervalo mínimo de 11 horas
            intervalo_minimo = timedelta(hours=11)

            # Verifica se a nova diária respeita o intervalo de 11h após outra diária
            if diaria_inicio < outra_fim + intervalo_minimo and diaria_inicio > outra_fim:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Você precisa de pelo menos 11 horas de descanso após a diária do dia {outra_diaria.data.strftime('%d/%m')}",
                )

            # Verifica se a nova diária respeita o intervalo de 11h antes da outra diária
            if diaria_fim > outra_inicio - intervalo_minimo and diaria_fim < outra_inicio:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Você precisa de pelo menos 11 horas de descanso antes da diária do dia {outra_diaria.data.strftime('%d/%m')}",
                )

            # Verifica sobreposição de horários
            if diaria_inicio < outra_fim and diaria_fim > outra_inicio:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Esta diária conflita com sua inscrição do dia {outra_diaria.data.strftime('%d/%m')}",
                )

        # Verifica se há vagas
        if diaria.vagas_disponiveis <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não há vagas disponíveis para esta diária",
            )

        return self.repository.create(pessoa_id, inscricao_data)

    def cancelar_inscricao(self, pessoa_id: int, inscricao_id: int) -> Inscricao:
        """Colaborador cancela sua própria inscrição."""
        inscricao = self.get_inscricao(inscricao_id)

        # Verifica se a inscrição pertence ao colaborador
        if inscricao.pessoa_id != pessoa_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para cancelar esta inscrição",
            )

        # Verifica se a diária ainda está aberta para cancelamentos
        if inscricao.diaria.status != StatusDiaria.ABERTA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível cancelar inscrição após o fechamento da diária",
            )

        # Verifica se pode cancelar
        if inscricao.status not in [StatusInscricao.PENDENTE, StatusInscricao.CONFIRMADA]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Esta inscrição não pode ser cancelada",
            )

        return self.repository.update_status(inscricao_id, StatusInscricao.CANCELADA)

    def atualizar_status(self, inscricao_id: int, novo_status: StatusInscricao) -> Inscricao:
        """Admin atualiza status de uma inscrição."""
        self.get_inscricao(inscricao_id)
        return self.repository.update_status(inscricao_id, novo_status)

    def listar_inscritos(self, diaria_id: int) -> List[Inscricao]:
        """Lista inscritos de uma diária (para admin)."""
        diaria = self.diaria_repository.get_by_id(diaria_id)
        if not diaria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diária não encontrada",
            )
        return self.repository.get_by_diaria(diaria_id)
