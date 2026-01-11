"""Endpoints para Relatórios Extras de Gestão de Pessoas."""
from datetime import date
from typing import Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.deps import get_db
from app.core.permissions import require_admin
from app.models.pessoa import Pessoa
from app.models.diaria import Diaria, Inscricao
from app.models.presenca import RegistroPresenca
from app.models.enums import StatusInscricao, TipoPessoa

router = APIRouter()


@router.get("/frequencia-colaborador")
def relatorio_frequencia_colaborador(
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Relatório de frequência por colaborador - presenças, faltas e taxa de comparecimento."""
    
    colaboradores = db.query(Pessoa).filter(
        Pessoa.tipo_pessoa == TipoPessoa.COLABORADOR,
        Pessoa.ativo == True
    ).all()
    
    result = []
    
    for colab in colaboradores:
        # Query base de inscrições
        query = db.query(Inscricao).filter(Inscricao.pessoa_id == colab.id)
        
        if data_inicio or data_fim:
            query = query.join(Diaria)
            if data_inicio:
                query = query.filter(Diaria.data >= data_inicio)
            if data_fim:
                query = query.filter(Diaria.data <= data_fim)
        
        # Total de inscrições confirmadas
        total_confirmadas = query.filter(
            Inscricao.status.in_([StatusInscricao.CONFIRMADA, StatusInscricao.CONCLUIDA])
        ).count()
        
        # Total de presenças
        presencas = db.query(RegistroPresenca).join(Inscricao).filter(
            Inscricao.pessoa_id == colab.id
        )
        if data_inicio or data_fim:
            presencas = presencas.join(Diaria)
            if data_inicio:
                presencas = presencas.filter(Diaria.data >= data_inicio)
            if data_fim:
                presencas = presencas.filter(Diaria.data <= data_fim)
        total_presencas = presencas.count()
        
        # Faltas
        total_faltas = max(0, total_confirmadas - total_presencas)
        
        # Taxa de comparecimento
        taxa = round((total_presencas / total_confirmadas) * 100, 1) if total_confirmadas > 0 else 0
        
        if total_confirmadas > 0:  # Só mostra quem teve inscrições
            result.append({
                "colaborador_id": colab.id,
                "nome": colab.nome,
                "email": colab.email,
                "telefone": colab.telefone,
                "total_confirmadas": total_confirmadas,
                "total_presencas": total_presencas,
                "total_faltas": total_faltas,
                "taxa_comparecimento": taxa,
                "classificacao": "Excelente" if taxa >= 90 else ("Bom" if taxa >= 70 else ("Regular" if taxa >= 50 else "Crítico")),
            })
    
    result = sorted(result, key=lambda x: x["taxa_comparecimento"], reverse=True)
    
    return {
        "total_colaboradores": len(result),
        "media_taxa": round(sum(r["taxa_comparecimento"] for r in result) / len(result), 1) if result else 0,
        "colaboradores": result,
    }


@router.get("/ranking-desempenho")
def relatorio_ranking_desempenho(
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    limite: int = Query(20, description="Número de colaboradores no ranking"),
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Ranking de desempenho - Top colaboradores por diárias concluídas."""
    
    query = db.query(
        Pessoa.id,
        Pessoa.nome,
        Pessoa.email,
        func.count(RegistroPresenca.id).label('total_presencas'),
        func.sum(Diaria.valor).label('valor_total')
    ).join(
        Inscricao, Inscricao.pessoa_id == Pessoa.id
    ).join(
        RegistroPresenca, RegistroPresenca.inscricao_id == Inscricao.id
    ).join(
        Diaria, Diaria.id == Inscricao.diaria_id
    ).filter(
        Pessoa.tipo_pessoa == TipoPessoa.COLABORADOR
    ).group_by(Pessoa.id)
    
    if data_inicio:
        query = query.filter(Diaria.data >= data_inicio)
    if data_fim:
        query = query.filter(Diaria.data <= data_fim)
    
    ranking = query.order_by(func.count(RegistroPresenca.id).desc()).limit(limite).all()
    
    result = []
    for i, (pessoa_id, nome, email, total, valor) in enumerate(ranking, 1):
        result.append({
            "posicao": i,
            "colaborador_id": pessoa_id,
            "nome": nome,
            "email": email,
            "total_diarias": total,
            "valor_total": float(valor) if valor else 0,
            "medalha": "🥇" if i == 1 else ("🥈" if i == 2 else ("🥉" if i == 3 else "")),
        })
    
    return {
        "periodo": {
            "inicio": str(data_inicio) if data_inicio else None,
            "fim": str(data_fim) if data_fim else None,
        },
        "ranking": result,
    }


@router.get("/historico-penalidades")
def relatorio_historico_penalidades(
    apenas_ativos: bool = Query(False, description="Mostrar apenas bloqueios ativos"),
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Histórico de penalidades/bloqueios aplicados a colaboradores."""
    
    query = db.query(Pessoa).filter(
        Pessoa.tipo_pessoa == TipoPessoa.COLABORADOR
    )
    
    if apenas_ativos:
        query = query.filter(Pessoa.bloqueado == True)
    else:
        query = query.filter(
            (Pessoa.bloqueado == True) | (Pessoa.motivo_bloqueio != None)
        )
    
    pessoas = query.order_by(Pessoa.bloqueado.desc()).all()
    
    ativos = 0
    result = []
    
    for pessoa in pessoas:
        if pessoa.bloqueado:
            ativos += 1
        
        result.append({
            "colaborador_id": pessoa.id,
            "nome": pessoa.nome,
            "email": pessoa.email,
            "bloqueado": pessoa.bloqueado,
            "motivo": pessoa.motivo_bloqueio,
            "bloqueado_ate": str(pessoa.bloqueado_ate) if pessoa.bloqueado_ate else None,
            "status": "🔴 Bloqueado" if pessoa.bloqueado else "🟢 Liberado",
        })
    
    return {
        "total_registros": len(result),
        "bloqueios_ativos": ativos,
        "penalidades": result,
    }


@router.get("/demanda-oferta")
def relatorio_demanda_oferta(
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Relatório de demanda vs oferta - vagas abertas vs inscrições."""
    
    query = db.query(Diaria)
    
    if data_inicio:
        query = query.filter(Diaria.data >= data_inicio)
    if data_fim:
        query = query.filter(Diaria.data <= data_fim)
    
    diarias = query.order_by(Diaria.data.desc()).all()
    
    total_vagas = 0
    total_inscricoes = 0
    vagas_nao_preenchidas = 0
    diarias_lotadas = 0
    
    por_empresa = {}
    dias_nomes = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    por_dia_semana = {i: {"dia": dias_nomes[i], "vagas": 0, "inscricoes": 0} for i in range(7)}
    
    result_diarias = []
    
    for diaria in diarias:
        inscricoes = db.query(Inscricao).filter(
            Inscricao.diaria_id == diaria.id,
            Inscricao.status.in_([StatusInscricao.CONFIRMADA, StatusInscricao.PENDENTE])
        ).count()
        
        total_vagas += diaria.vagas
        total_inscricoes += inscricoes
        
        vagas_restantes = diaria.vagas - inscricoes
        if vagas_restantes > 0:
            vagas_nao_preenchidas += vagas_restantes
        if vagas_restantes <= 0:
            diarias_lotadas += 1
        
        emp_nome = diaria.empresa.nome
        if emp_nome not in por_empresa:
            por_empresa[emp_nome] = {"vagas": 0, "inscricoes": 0}
        por_empresa[emp_nome]["vagas"] += diaria.vagas
        por_empresa[emp_nome]["inscricoes"] += inscricoes
        
        dia_semana = diaria.data.weekday()
        por_dia_semana[dia_semana]["vagas"] += diaria.vagas
        por_dia_semana[dia_semana]["inscricoes"] += inscricoes
        
        result_diarias.append({
            "id": diaria.id,
            "titulo": diaria.titulo,
            "data": str(diaria.data),
            "empresa": emp_nome,
            "vagas": diaria.vagas,
            "inscricoes": inscricoes,
            "vagas_restantes": max(0, vagas_restantes),
            "status": "🔴 Lotada" if vagas_restantes <= 0 else ("🟡 Parcial" if inscricoes > 0 else "🟢 Vazia"),
        })
    
    return {
        "resumo": {
            "total_vagas": total_vagas,
            "total_inscricoes": total_inscricoes,
            "taxa_preenchimento": round((total_inscricoes / total_vagas) * 100, 1) if total_vagas > 0 else 0,
            "vagas_nao_preenchidas": vagas_nao_preenchidas,
            "diarias_lotadas": diarias_lotadas,
            "total_diarias": len(diarias),
        },
        "por_empresa": [{"empresa": k, **v} for k, v in sorted(por_empresa.items(), key=lambda x: x[1]["vagas"], reverse=True)],
        "por_dia_semana": list(por_dia_semana.values()),
        "diarias": result_diarias[:50],
    }


@router.get("/uso-fretado")
def relatorio_uso_fretado(
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Relatório de uso do transporte fretado por rota."""
    from app.models.rota import Rota, PontoParada
    
    rotas = db.query(Rota).filter(Rota.ativo == True).all()
    
    result = []
    total_colaboradores = 0
    
    for rota in rotas:
        pontos = db.query(PontoParada).filter(PontoParada.rota_id == rota.id).all()
        
        colaboradores_rota = 0
        pontos_info = []
        
        for ponto in pontos:
            qtd = db.query(Pessoa).filter(
                Pessoa.ponto_parada_id == ponto.id,
                Pessoa.tipo_pessoa == TipoPessoa.COLABORADOR,
                Pessoa.ativo == True
            ).count()
            
            colaboradores_rota += qtd
            pontos_info.append({
                "ponto_id": ponto.id,
                "nome": ponto.nome,
                "endereco": ponto.endereco,
                "colaboradores": qtd,
            })
        
        total_colaboradores += colaboradores_rota
        
        result.append({
            "rota_id": rota.id,
            "nome": rota.nome,
            "descricao": rota.descricao,
            "horario_ida": str(rota.horario_ida) if rota.horario_ida else None,
            "horario_volta": str(rota.horario_volta) if rota.horario_volta else None,
            "total_pontos": len(pontos),
            "total_colaboradores": colaboradores_rota,
            "pontos": sorted(pontos_info, key=lambda x: x["colaboradores"], reverse=True),
        })
    
    sem_rota = db.query(Pessoa).filter(
        Pessoa.ponto_parada_id == None,
        Pessoa.tipo_pessoa == TipoPessoa.COLABORADOR,
        Pessoa.ativo == True
    ).count()
    
    return {
        "resumo": {
            "total_rotas": len(rotas),
            "total_colaboradores_fretado": total_colaboradores,
            "colaboradores_sem_rota": sem_rota,
        },
        "rotas": sorted(result, key=lambda x: x["total_colaboradores"], reverse=True),
    }
