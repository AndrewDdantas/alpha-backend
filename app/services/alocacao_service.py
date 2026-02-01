"""
Serviço de Alocação de Veículos para Diárias.
Responsável por distribuir colaboradores em veículos e calcular horários de passagem.
"""
from datetime import datetime, time, timedelta, date
from typing import List, Dict, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.alocacao import AlocacaoDiaria, AlocacaoColaborador
from app.models.diaria import Diaria, Inscricao
from app.models.veiculo import Veiculo
from app.models.pessoa import Pessoa
from app.models.rota import PontoParada
from app.models.enums import StatusDiaria, StatusInscricao
from app.schemas.alocacao import (
    GerarAlocacaoResponse, AlocacaoDiariaResponse, AlocacaoColaboradorResponse,
    MinhaAlocacaoResponse
)
from app.services.google_service import google_maps_service


class AlocacaoService:
    """Serviço para gerenciar alocação de veículos."""

    def __init__(self, db: Session):
        self.db = db

    def get_diaria(self, diaria_id: int) -> Diaria:
        """Busca diária com inscrições."""
        diaria = (
            self.db.query(Diaria)
            .options(
                joinedload(Diaria.inscricoes).joinedload(Inscricao.pessoa).joinedload(Pessoa.ponto_parada)
            )
            .filter(Diaria.id == diaria_id)
            .first()
        )
        if not diaria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diária não encontrada",
            )
        return diaria

    def get_veiculos_disponiveis(self) -> List[Veiculo]:
        """Retorna veículos ativos ordenados por capacidade."""
        return (
            self.db.query(Veiculo)
            .filter(Veiculo.ativo == True)
            .order_by(Veiculo.capacidade.desc())
            .all()
        )

    def get_veiculos_disponiveis_para_diaria(self, diaria_id: int) -> List[Veiculo]:
        """
        Retorna veículos ativos que NÃO estão alocados em outras diárias
        na mesma data e horário conflitante.
        """
        # Busca a diária
        diaria = self.db.query(Diaria).filter(Diaria.id == diaria_id).first()
        if not diaria:
            return self.get_veiculos_disponiveis()
        
        # Busca IDs de veículos já alocados em diárias na mesma data
        veiculos_ocupados = (
            self.db.query(AlocacaoDiaria.veiculo_id)
            .join(Diaria, AlocacaoDiaria.diaria_id == Diaria.id)
            .filter(
                Diaria.data == diaria.data,
                AlocacaoDiaria.diaria_id != diaria_id,  # Exclui a própria diária
            )
            .distinct()
            .all()
        )
        
        veiculos_ocupados_ids = [v[0] for v in veiculos_ocupados]
        
        # Retorna veículos não ocupados
        query = (
            self.db.query(Veiculo)
            .filter(Veiculo.ativo == True)
        )
        
        if veiculos_ocupados_ids:
            query = query.filter(Veiculo.id.notin_(veiculos_ocupados_ids))
        
        return query.order_by(Veiculo.capacidade.desc()).all()

    def get_alocacoes_diaria(self, diaria_id: int) -> List[AlocacaoDiariaResponse]:
        """Retorna alocações existentes de uma diária."""
        alocacoes = (
            self.db.query(AlocacaoDiaria)
            .options(
                joinedload(AlocacaoDiaria.veiculo),
                joinedload(AlocacaoDiaria.colaboradores)
                    .joinedload(AlocacaoColaborador.inscricao)
                    .joinedload(Inscricao.pessoa),
                joinedload(AlocacaoDiaria.colaboradores)
                    .joinedload(AlocacaoColaborador.ponto_parada),
            )
            .filter(AlocacaoDiaria.diaria_id == diaria_id)
            .all()
        )

        result = []
        for aloc in alocacoes:
            colaboradores = []
            for col in aloc.colaboradores:
                colaboradores.append(AlocacaoColaboradorResponse(
                    id=col.id,
                    inscricao_id=col.inscricao_id,
                    ponto_parada_id=col.ponto_parada_id,
                    horario_estimado=col.horario_estimado.strftime("%H:%M") if col.horario_estimado else None,
                    ordem_embarque=col.ordem_embarque,
                    pessoa_nome=col.inscricao.pessoa.nome if col.inscricao and col.inscricao.pessoa else None,
                    ponto_nome=col.ponto_parada.nome if col.ponto_parada else None,
                ))

            result.append(AlocacaoDiariaResponse(
                id=aloc.id,
                diaria_id=aloc.diaria_id,
                veiculo_id=aloc.veiculo_id,
                rota_id=aloc.rota_id,
                horario_saida=aloc.horario_saida.strftime("%H:%M") if aloc.horario_saida else None,
                veiculo_placa=aloc.veiculo.placa if aloc.veiculo else None,
                veiculo_modelo=aloc.veiculo.modelo if aloc.veiculo else None,
                motorista=aloc.veiculo.motorista if aloc.veiculo else None,
                telefone_motorista=aloc.veiculo.telefone_motorista if aloc.veiculo else None,
                colaboradores=colaboradores,
            ))

        return result

    def gerar_alocacao_automatica(
        self,
        diaria_id: int,
        horario_saida: str,
    ) -> GerarAlocacaoResponse:
        """
        Gera alocação automática de veículos para uma diária.

        1. Busca inscrições confirmadas/pendentes
        2. Agrupa por ponto de parada
        3. Distribui em veículos disponíveis
        4. Calcula horários de passagem
        """
        diaria = self.get_diaria(diaria_id)

        # Verifica se diária está fechada
        if diaria.status not in [StatusDiaria.FECHADA, StatusDiaria.ABERTA]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Diária precisa estar fechada ou aberta para gerar alocação",
            )

        # Remove alocações anteriores
        self.db.query(AlocacaoDiaria).filter(AlocacaoDiaria.diaria_id == diaria_id).delete()
        self.db.commit()

        # Busca inscrições ativas
        inscricoes = [
            i for i in diaria.inscricoes
            if i.status in [StatusInscricao.PENDENTE, StatusInscricao.CONFIRMADA]
        ]

        if not inscricoes:
            return GerarAlocacaoResponse(
                sucesso=False,
                mensagem="Não há inscrições ativas para esta diária",
                alocacoes=[],
            )

        # Separa colaboradores com e sem ponto
        colaboradores_com_ponto = []
        colaboradores_sem_ponto = []

        for inscricao in inscricoes:
            if inscricao.pessoa and inscricao.pessoa.ponto_parada:
                colaboradores_com_ponto.append(inscricao)
            else:
                colaboradores_sem_ponto.append(
                    inscricao.pessoa.nome if inscricao.pessoa else f"Inscricao #{inscricao.id}"
                )

        # Agrupa por ponto de parada
        por_ponto: Dict[int, List[Inscricao]] = {}
        for inscricao in colaboradores_com_ponto:
            ponto_id = inscricao.pessoa.ponto_parada_id
            if ponto_id not in por_ponto:
                por_ponto[ponto_id] = []
            por_ponto[ponto_id].append(inscricao)

        # Ordena pontos pela ordem na rota
        pontos_ordenados = sorted(
            por_ponto.keys(),
            key=lambda pid: self._get_ordem_ponto(pid)
        )

        # Busca veículos disponíveis (exclui os já alocados em outras diárias na mesma data)
        veiculos = self.get_veiculos_disponiveis_para_diaria(diaria_id)
        if not veiculos:
            return GerarAlocacaoResponse(
                sucesso=False,
                mensagem="Não há veículos disponíveis para esta data (todos já estão alocados em outras diárias)",
                alocacoes=[],
                colaboradores_sem_ponto=colaboradores_sem_ponto,
            )

        # Distribui colaboradores em veículos
        alocacoes_criadas = []
        colaboradores_restantes = list(colaboradores_com_ponto)
        veiculo_idx = 0

        while colaboradores_restantes and veiculo_idx < len(veiculos):
            veiculo = veiculos[veiculo_idx]

            # Cria alocação para este veículo
            horario_obj = self._parse_time(horario_saida)
            alocacao = AlocacaoDiaria(
                diaria_id=diaria_id,
                veiculo_id=veiculo.id,
                horario_saida=horario_obj,
            )
            self.db.add(alocacao)
            self.db.flush()

            # Preenche veículo até a capacidade
            colaboradores_neste = []
            for _ in range(min(veiculo.capacidade, len(colaboradores_restantes))):
                inscricao = colaboradores_restantes.pop(0)
                colaboradores_neste.append(inscricao)

            # Calcula horários de passagem
            horarios = self._calcular_horarios_passagem(
                colaboradores_neste,
                horario_obj,
                pontos_ordenados,
            )

            # Cria alocações de colaboradores
            for ordem, (inscricao, horario) in enumerate(horarios):
                aloc_col = AlocacaoColaborador(
                    alocacao_diaria_id=alocacao.id,
                    inscricao_id=inscricao.id,
                    ponto_parada_id=inscricao.pessoa.ponto_parada_id if inscricao.pessoa else None,
                    horario_estimado=horario,
                    ordem_embarque=ordem + 1,
                )
                self.db.add(aloc_col)

            alocacoes_criadas.append(alocacao)
            veiculo_idx += 1

        self.db.commit()

        # Monta resposta
        return GerarAlocacaoResponse(
            sucesso=True,
            mensagem=f"Alocação gerada com sucesso! {len(alocacoes_criadas)} veículo(s) utilizados.",
            alocacoes=self.get_alocacoes_diaria(diaria_id),
            veiculos_usados=len(alocacoes_criadas),
            colaboradores_alocados=len(colaboradores_com_ponto),
            colaboradores_sem_ponto=colaboradores_sem_ponto,
        )

    def _get_ordem_ponto(self, ponto_id: int) -> int:
        """Retorna a ordem do ponto na rota."""
        ponto = self.db.query(PontoParada).filter(PontoParada.id == ponto_id).first()
        return ponto.ordem if ponto else 999

    def _parse_time(self, time_str: str) -> time:
        """Converte string HH:MM para time."""
        try:
            parts = time_str.split(":")
            return time(int(parts[0]), int(parts[1]))
        except:
            return time(7, 0)

    def _calcular_horarios_passagem(
        self,
        colaboradores: List[Inscricao],
        horario_saida: time,
        pontos_ordenados: List[int],
    ) -> List[Tuple[Inscricao, time]]:
        """
        Calcula horário estimado de passagem em cada ponto.
        Usa Google Maps API para tempo de viagem real entre pontos.
        """
        resultado = []
        tempo_atual = datetime.combine(date.today(), horario_saida)
        MINUTOS_POR_PARADA = 0  # Tempo de embarque (desabilitado)
        MINUTOS_VIAGEM_PADRAO = 10  # Fallback se Google Maps falhar

        # Agrupa colaboradores por ponto
        por_ponto: Dict[int, List[Inscricao]] = {}
        for colab in colaboradores:
            ponto_id = colab.pessoa.ponto_parada_id if colab.pessoa else None
            if ponto_id:
                if ponto_id not in por_ponto:
                    por_ponto[ponto_id] = []
                por_ponto[ponto_id].append(colab)

        # Cache de pontos de parada
        pontos_cache: Dict[int, PontoParada] = {}
        for ponto_id in pontos_ordenados:
            ponto = self.db.query(PontoParada).filter(PontoParada.id == ponto_id).first()
            if ponto:
                pontos_cache[ponto_id] = ponto

        ponto_anterior_id = None

        # Processa na ordem dos pontos
        for ponto_id in pontos_ordenados:
            if ponto_id not in por_ponto:
                continue

            minutos_viagem = MINUTOS_VIAGEM_PADRAO

            # Calcula tempo real usando Google Maps
            if ponto_anterior_id and ponto_anterior_id in pontos_cache and ponto_id in pontos_cache:
                ponto_ant = pontos_cache[ponto_anterior_id]
                ponto_atual = pontos_cache[ponto_id]

                if ponto_ant.latitude and ponto_ant.longitude and ponto_atual.latitude and ponto_atual.longitude:
                    try:
                        import asyncio
                        
                        # Executa chamada async de forma sincrona
                        loop = asyncio.new_event_loop()
                        directions = loop.run_until_complete(
                            google_maps_service.get_route_directions(
                                origin=(ponto_ant.latitude, ponto_ant.longitude),
                                destination=(ponto_atual.latitude, ponto_atual.longitude),
                            )
                        )
                        loop.close()

                        if directions.get("success"):
                            minutos_viagem = directions["duracao_total_minutos"]
                    except Exception as e:
                        print(f"Google Maps API error: {e}")
                        # Usa tempo padrão em caso de falha

            # Adiciona tempo de viagem até este ponto
            tempo_atual += timedelta(minutes=minutos_viagem)

            # Atribui horário para todos neste ponto
            horario_passagem = tempo_atual.time()
            for colab in por_ponto[ponto_id]:
                resultado.append((colab, horario_passagem))

            # Adiciona tempo de parada
            tempo_atual += timedelta(minutes=MINUTOS_POR_PARADA)
            ponto_anterior_id = ponto_id

        return resultado

    def get_minhas_alocacoes(self, pessoa_id: int) -> List[MinhaAlocacaoResponse]:
        """Retorna alocações do colaborador para diárias futuras."""
        alocacoes = (
            self.db.query(AlocacaoColaborador)
            .options(
                joinedload(AlocacaoColaborador.alocacao_diaria)
                    .joinedload(AlocacaoDiaria.veiculo),
                joinedload(AlocacaoColaborador.alocacao_diaria)
                    .joinedload(AlocacaoDiaria.diaria),
                joinedload(AlocacaoColaborador.ponto_parada),
                joinedload(AlocacaoColaborador.inscricao),
            )
            .join(AlocacaoColaborador.inscricao)
            .filter(Inscricao.pessoa_id == pessoa_id)
            .join(AlocacaoColaborador.alocacao_diaria)
            .join(AlocacaoDiaria.diaria)
            .filter(Diaria.data >= date.today())
            .all()
        )

        resultado = []
        for aloc in alocacoes:
            diaria = aloc.alocacao_diaria.diaria
            veiculo = aloc.alocacao_diaria.veiculo
            ponto = aloc.ponto_parada

            resultado.append(MinhaAlocacaoResponse(
                diaria_id=diaria.id,
                diaria_titulo=diaria.titulo,
                diaria_data=diaria.data.isoformat(),
                diaria_local=diaria.local,
                veiculo_placa=veiculo.placa if veiculo else "N/A",
                veiculo_modelo=veiculo.modelo if veiculo else "N/A",
                veiculo_cor=veiculo.cor if veiculo else None,
                motorista=veiculo.motorista if veiculo else None,
                telefone_motorista=veiculo.telefone_motorista if veiculo else None,
                ponto_nome=ponto.nome if ponto else None,
                ponto_endereco=ponto.endereco if ponto else None,
                horario_estimado=aloc.horario_estimado.strftime("%H:%M") if aloc.horario_estimado else None,
                ordem_embarque=aloc.ordem_embarque,
            ))

        return resultado
