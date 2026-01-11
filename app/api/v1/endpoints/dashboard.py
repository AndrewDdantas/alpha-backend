"""Endpoint para Dashboard Executivo."""
from datetime import date, datetime, timedelta
from typing import Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.deps import get_db
from app.core.permissions import require_admin
from app.models.pessoa import Pessoa
from app.models.diaria import Diaria, Inscricao
from app.models.empresa import Empresa
from app.models.presenca import RegistroPresenca
from app.models.enums import StatusInscricao, StatusDiaria, TipoPessoa

router = APIRouter()


@router.get("/executive")
def dashboard_executive(
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Dashboard executivo com métricas consolidadas."""
    
    hoje = date.today()
    inicio_mes = hoje.replace(day=1)
    inicio_mes_anterior = (inicio_mes - timedelta(days=1)).replace(day=1)
    fim_mes_anterior = inicio_mes - timedelta(days=1)
    
    # === MÉTRICAS GERAIS ===
    total_colaboradores = db.query(Pessoa).filter(
        Pessoa.tipo_pessoa == TipoPessoa.COLABORADOR,
        Pessoa.ativo == True
    ).count()
    
    colaboradores_bloqueados = db.query(Pessoa).filter(
        Pessoa.tipo_pessoa == TipoPessoa.COLABORADOR,
        Pessoa.bloqueado == True
    ).count()
    
    # === DIÁRIAS DO MÊS ===
    diarias_mes = db.query(Diaria).filter(
        Diaria.data >= inicio_mes,
        Diaria.data <= hoje
    ).all()
    
    total_diarias_mes = len(diarias_mes)
    total_vagas_mes = sum(d.vagas for d in diarias_mes)
    
    # Presenças do mês
    presencas_mes = db.query(func.count(RegistroPresenca.id)).join(
        Inscricao, RegistroPresenca.inscricao_id == Inscricao.id
    ).join(
        Diaria, Inscricao.diaria_id == Diaria.id
    ).filter(
        Diaria.data >= inicio_mes,
        Diaria.data <= hoje
    ).scalar() or 0
    
    # Valor pago no mês
    valor_mes = Decimal('0.00')
    for diaria in diarias_mes:
        presencas = db.query(RegistroPresenca).join(Inscricao).filter(
            Inscricao.diaria_id == diaria.id
        ).count()
        if diaria.valor:
            valor_mes += diaria.valor * presencas
    
    # === MÊS ANTERIOR (para comparativo) ===
    diarias_mes_anterior = db.query(Diaria).filter(
        Diaria.data >= inicio_mes_anterior,
        Diaria.data <= fim_mes_anterior
    ).all()
    
    total_diarias_ant = len(diarias_mes_anterior)
    presencas_ant = db.query(func.count(RegistroPresenca.id)).join(
        Inscricao, RegistroPresenca.inscricao_id == Inscricao.id
    ).join(
        Diaria, Inscricao.diaria_id == Diaria.id
    ).filter(
        Diaria.data >= inicio_mes_anterior,
        Diaria.data <= fim_mes_anterior
    ).scalar() or 0
    
    # === HOJE ===
    diarias_hoje = db.query(Diaria).filter(Diaria.data == hoje).count()
    diarias_abertas = db.query(Diaria).filter(
        Diaria.status == StatusDiaria.ABERTA,
        Diaria.data >= hoje
    ).count()
    
    # === POR EMPRESA (TOP 5) ===
    empresas_stats = {}
    for diaria in diarias_mes:
        emp_nome = diaria.empresa.nome
        if emp_nome not in empresas_stats:
            empresas_stats[emp_nome] = {"diarias": 0, "valor": Decimal('0.00')}
        empresas_stats[emp_nome]["diarias"] += 1
        
        presencas = db.query(RegistroPresenca).join(Inscricao).filter(
            Inscricao.diaria_id == diaria.id
        ).count()
        if diaria.valor:
            empresas_stats[emp_nome]["valor"] += diaria.valor * presencas
    
    top_empresas = sorted(
        [{"empresa": k, "diarias": v["diarias"], "valor": float(v["valor"])} 
         for k, v in empresas_stats.items()],
        key=lambda x: x["valor"],
        reverse=True
    )[:5]
    
    # === ÚLTIMOS 7 DIAS (para gráfico) ===
    ultimos_7_dias = []
    for i in range(6, -1, -1):
        dia = hoje - timedelta(days=i)
        
        diarias_dia = db.query(Diaria).filter(Diaria.data == dia).count()
        presencas_dia = db.query(func.count(RegistroPresenca.id)).join(
            Inscricao, RegistroPresenca.inscricao_id == Inscricao.id
        ).join(
            Diaria, Inscricao.diaria_id == Diaria.id
        ).filter(Diaria.data == dia).scalar() or 0
        
        ultimos_7_dias.append({
            "data": dia.strftime("%d/%m"),
            "dia_semana": ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"][dia.weekday()],
            "diarias": diarias_dia,
            "presencas": presencas_dia,
        })
    
    # === TAXA DE FREQUÊNCIA ===
    total_inscricoes_mes = db.query(func.count(Inscricao.id)).join(
        Diaria, Inscricao.diaria_id == Diaria.id
    ).filter(
        Diaria.data >= inicio_mes,
        Diaria.data <= hoje,
        Inscricao.status.in_([StatusInscricao.CONFIRMADA, StatusInscricao.CONCLUIDA])
    ).scalar() or 0
    
    taxa_frequencia = round((presencas_mes / total_inscricoes_mes) * 100, 1) if total_inscricoes_mes > 0 else 0
    
    # === VARIAÇÕES ===
    variacao_diarias = round(((total_diarias_mes - total_diarias_ant) / total_diarias_ant) * 100, 1) if total_diarias_ant > 0 else 0
    variacao_presencas = round(((presencas_mes - presencas_ant) / presencas_ant) * 100, 1) if presencas_ant > 0 else 0
    
    return {
        "resumo": {
            "total_colaboradores": total_colaboradores,
            "colaboradores_bloqueados": colaboradores_bloqueados,
            "diarias_hoje": diarias_hoje,
            "diarias_abertas": diarias_abertas,
        },
        "mes_atual": {
            "nome": hoje.strftime("%B %Y").title(),
            "total_diarias": total_diarias_mes,
            "total_vagas": total_vagas_mes,
            "total_presencas": presencas_mes,
            "valor_total": float(valor_mes),
            "taxa_frequencia": taxa_frequencia,
            "variacao_diarias": variacao_diarias,
            "variacao_presencas": variacao_presencas,
        },
        "top_empresas": top_empresas,
        "ultimos_7_dias": ultimos_7_dias,
    }


@router.get("/hoje")
def dashboard_hoje(
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Dashboard do dia atual."""
    
    hoje = date.today()
    
    diarias_hoje = db.query(Diaria).filter(Diaria.data == hoje).all()
    
    resultado = []
    for diaria in diarias_hoje:
        inscricoes = db.query(Inscricao).filter(
            Inscricao.diaria_id == diaria.id,
            Inscricao.status == StatusInscricao.CONFIRMADA
        ).count()
        
        presencas = db.query(RegistroPresenca).join(Inscricao).filter(
            Inscricao.diaria_id == diaria.id
        ).count()
        
        resultado.append({
            "id": diaria.id,
            "titulo": diaria.titulo,
            "empresa": diaria.empresa.nome,
            "horario": str(diaria.horario_inicio) if diaria.horario_inicio else None,
            "status": diaria.status.value,
            "vagas": diaria.vagas,
            "inscricoes": inscricoes,
            "presencas": presencas,
            "supervisor": diaria.supervisor.nome if diaria.supervisor else None,
        })
    
    return {
        "data": str(hoje),
        "total_diarias": len(resultado),
        "diarias": resultado,
    }
