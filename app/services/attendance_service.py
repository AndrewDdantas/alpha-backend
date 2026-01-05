from datetime import date, datetime, timedelta
from typing import List

from sqlalchemy.orm import Session

from app.models.diaria import Inscricao
from app.models.enums import StatusInscricao, StatusDiaria
from app.models.pessoa import Pessoa
from app.repositories.diaria_repository import InscricaoRepository, DiariaRepository
from app.repositories.pessoa_repository import PessoaRepository
from app.repositories.presenca_repository import PresencaRepository


class AttendanceService:
    """Serviço para gerenciar presenças e penalidades."""

    def __init__(self, db: Session):
        self.db = db
        self.inscricao_repo = InscricaoRepository(db)
        self.diaria_repo = DiariaRepository(db)
        self.pessoa_repo = PessoaRepository(db)
        self.presenca_repo = PresencaRepository(db)

    def marcar_faltas_automaticas(self) -> dict:
        """
        Marca como FALTA inscrições confirmadas sem presença registrada
        em diárias que já terminaram.
        Retorna estatísticas do processamento.
        """
        hoje = date.today()
        agora = datetime.now()
        
        # Busca diárias concluídas ou em andamento que já passaram do horário
        diarias = self.diaria_repo.get_all(
            status=StatusDiaria.CONCLUIDA,
            skip=0,
            limit=1000
        )
        
        # Também busca diárias em andamento que já passaram do horário de fim
        diarias_em_andamento = self.diaria_repo.get_all(
            status=StatusDiaria.EM_ANDAMENTO,
            skip=0,
            limit=1000
        )
        
        diarias_para_processar = []
        
        # Filtra diárias que já terminaram
        for diaria in list(diarias) + list(diarias_em_andamento):
            if diaria.data < hoje:
                diarias_para_processar.append(diaria)
            elif diaria.data == hoje and diaria.horario_fim:
                horario_fim = datetime.combine(diaria.data, diaria.horario_fim)
                if agora > horario_fim:
                    diarias_para_processar.append(diaria)
        
        total_faltas = 0
        total_penalidades = 0
        
        for diaria in diarias_para_processar:
            # Busca inscrições confirmadas
            inscricoes = self.inscricao_repo.get_by_diaria(diaria.id)
            
            for inscricao in inscricoes:
                # Só processa se estiver confirmada
                if inscricao.status != StatusInscricao.CONFIRMADA:
                    continue
                
                # Verifica se tem presença registrada
                presenca = self.presenca_repo.get_by_inscricao(inscricao.id)
                
                if not presenca:
                    # Marca como falta
                    self.inscricao_repo.update_status(inscricao.id, StatusInscricao.FALTA)
                    total_faltas += 1
                    
                    # Aplica penalidade de 2 dias
                    self.aplicar_penalidade(inscricao.pessoa_id, dias=2)
                    total_penalidades += 1
        
        return {
            "diarias_processadas": len(diarias_para_processar),
            "total_faltas": total_faltas,
            "total_penalidades": total_penalidades,
        }

    def aplicar_penalidade(self, pessoa_id: int, dias: int = 2, motivo: str = None) -> Pessoa:
        """
        Aplica penalidade de bloqueio temporário a uma pessoa.
        
        Args:
            pessoa_id: ID da pessoa
            dias: Número de dias de bloqueio (padrão: 2)
            motivo: Motivo do bloqueio (opcional)
        """
        pessoa = self.pessoa_repo.get_by_id(pessoa_id)
        
        if not pessoa:
            return None
        
        # Calcula data de desbloqueio
        data_desbloqueio = date.today() + timedelta(days=dias)
        
        # Se já estava bloqueado, estende o bloqueio
        if pessoa.bloqueado and pessoa.bloqueado_ate and pessoa.bloqueado_ate > date.today():
            data_desbloqueio = pessoa.bloqueado_ate + timedelta(days=dias)
        
        # Atualiza pessoa
        pessoa.bloqueado = True
        pessoa.bloqueado_ate = data_desbloqueio
        pessoa.motivo_bloqueio = motivo or "Falta em diária sem justificativa"
        
        self.db.commit()
        self.db.refresh(pessoa)
        
        return pessoa

    def remover_penalidade(self, pessoa_id: int) -> Pessoa:
        """Remove penalidade de uma pessoa (uso administrativo)."""
        pessoa = self.pessoa_repo.get_by_id(pessoa_id)
        
        if not pessoa:
            return None
        
        pessoa.bloqueado = False
        pessoa.bloqueado_ate = None
        pessoa.motivo_bloqueio = None
        
        self.db.commit()
        self.db.refresh(pessoa)
        
        return pessoa
