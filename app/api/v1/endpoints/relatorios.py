"""Endpoints para Relatórios Financeiros."""
from datetime import date, datetime
from typing import Optional, List
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
from app.models.enums import StatusInscricao, StatusDiaria

router = APIRouter()


@router.get("/diarias")
def relatorio_diarias(
    data_inicio: Optional[date] = Query(None, description="Data inicial"),
    data_fim: Optional[date] = Query(None, description="Data final"),
    empresa_id: Optional[int] = Query(None, description="Filtrar por empresa"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Relatório de diárias com totais financeiros."""
    
    query = db.query(Diaria)
    
    if data_inicio:
        query = query.filter(Diaria.data >= data_inicio)
    if data_fim:
        query = query.filter(Diaria.data <= data_fim)
    if empresa_id:
        query = query.filter(Diaria.empresa_id == empresa_id)
    if status:
        query = query.filter(Diaria.status == status)
    
    diarias = query.order_by(Diaria.data.desc()).all()
    
    # Calcula totais
    total_diarias = len(diarias)
    total_vagas = sum(d.vagas for d in diarias)
    total_inscricoes = 0
    total_presencas = 0
    total_valor = Decimal('0.00')
    
    result_diarias = []
    
    for diaria in diarias:
        # Conta inscrições confirmadas
        inscricoes = db.query(Inscricao).filter(
            Inscricao.diaria_id == diaria.id,
            Inscricao.status == StatusInscricao.CONFIRMADA
        ).count()
        
        # Conta presenças
        presencas = db.query(RegistroPresenca).join(Inscricao).filter(
            Inscricao.diaria_id == diaria.id
        ).count()
        
        total_inscricoes += inscricoes
        total_presencas += presencas
        
        # Calcula valor apenas para quem teve presença registrada
        if diaria.valor:
            total_valor += diaria.valor * presencas
        
        result_diarias.append({
            "id": diaria.id,
            "titulo": diaria.titulo,
            "data": str(diaria.data),
            "horario_inicio": str(diaria.horario_inicio) if diaria.horario_inicio else None,
            "empresa": diaria.empresa.nome,
            "status": diaria.status.value,
            "vagas": diaria.vagas,
            "inscricoes": inscricoes,
            "presencas": presencas,
            "valor_unitario": float(diaria.valor) if diaria.valor else None,
            "valor_total": float(diaria.valor * presencas) if diaria.valor else 0,  # Pagamento só para quem teve presença
            "supervisor": diaria.supervisor.nome if diaria.supervisor else None,
        })
    
    return {
        "resumo": {
            "total_diarias": total_diarias,
            "total_vagas": total_vagas,
            "total_inscricoes": total_inscricoes,
            "total_presencas": total_presencas,
            "total_valor": float(total_valor),
            "taxa_presenca": round(total_presencas / total_inscricoes * 100, 1) if total_inscricoes > 0 else 0,
        },
        "diarias": result_diarias,
    }


@router.get("/presencas")
def relatorio_presencas(
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    empresa_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Relatório de presenças por colaborador."""
    
    query = db.query(
        RegistroPresenca,
        Inscricao,
        Diaria,
        Pessoa
    ).join(
        Inscricao, RegistroPresenca.inscricao_id == Inscricao.id
    ).join(
        Diaria, Inscricao.diaria_id == Diaria.id
    ).join(
        Pessoa, Inscricao.pessoa_id == Pessoa.id
    )
    
    if data_inicio:
        query = query.filter(Diaria.data >= data_inicio)
    if data_fim:
        query = query.filter(Diaria.data <= data_fim)
    if empresa_id:
        query = query.filter(Diaria.empresa_id == empresa_id)
    
    records = query.order_by(Diaria.data.desc()).all()
    
    # Agrupar por pessoa
    pessoas_presencas = {}
    for registro, inscricao, diaria, pessoa in records:
        if pessoa.id not in pessoas_presencas:
            pessoas_presencas[pessoa.id] = {
                "pessoa_id": pessoa.id,
                "nome": pessoa.nome,
                "cpf": pessoa.cpf,
                "email": pessoa.email,
                "telefone": pessoa.telefone,
                "total_presencas": 0,
                "valor_total": Decimal('0.00'),
                "diarias": [],
            }
        
        pessoas_presencas[pessoa.id]["total_presencas"] += 1
        if diaria.valor:
            pessoas_presencas[pessoa.id]["valor_total"] += diaria.valor
        
        pessoas_presencas[pessoa.id]["diarias"].append({
            "diaria_id": diaria.id,
            "titulo": diaria.titulo,
            "data": str(diaria.data),
            "empresa": diaria.empresa.nome,
            "valor": float(diaria.valor) if diaria.valor else None,
            "horario_registro": registro.horario_registro.isoformat(),
        })
    
    result = list(pessoas_presencas.values())
    for r in result:
        r["valor_total"] = float(r["valor_total"])
    
    return {
        "total_pessoas": len(result),
        "total_presencas": sum(r["total_presencas"] for r in result),
        "total_valor": sum(r["valor_total"] for r in result),
        "colaboradores": sorted(result, key=lambda x: x["total_presencas"], reverse=True),
    }


@router.get("/empresas")
def relatorio_por_empresa(
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Relatório consolidado por empresa."""
    
    query = db.query(Diaria)
    
    if data_inicio:
        query = query.filter(Diaria.data >= data_inicio)
    if data_fim:
        query = query.filter(Diaria.data <= data_fim)
    
    diarias = query.all()
    
    empresas_stats = {}
    
    for diaria in diarias:
        emp_id = diaria.empresa_id
        if emp_id not in empresas_stats:
            empresas_stats[emp_id] = {
                "empresa_id": emp_id,
                "nome": diaria.empresa.nome,
                "total_diarias": 0,
                "total_vagas": 0,
                "total_inscricoes": 0,
                "total_presencas": 0,
                "valor_total": Decimal('0.00'),
            }
        
        empresas_stats[emp_id]["total_diarias"] += 1
        empresas_stats[emp_id]["total_vagas"] += diaria.vagas
        
        inscricoes = db.query(Inscricao).filter(
            Inscricao.diaria_id == diaria.id,
            Inscricao.status == StatusInscricao.CONFIRMADA
        ).count()
        
        presencas = db.query(RegistroPresenca).join(Inscricao).filter(
            Inscricao.diaria_id == diaria.id
        ).count()
        
        empresas_stats[emp_id]["total_inscricoes"] += inscricoes
        empresas_stats[emp_id]["total_presencas"] += presencas
        
        # Valor total apenas para quem teve presença
        if diaria.valor:
            empresas_stats[emp_id]["valor_total"] += diaria.valor * presencas
    
    result = list(empresas_stats.values())
    for r in result:
        r["valor_total"] = float(r["valor_total"])
        r["taxa_presenca"] = round(r["total_presencas"] / r["total_inscricoes"] * 100, 1) if r["total_inscricoes"] > 0 else 0
    
    return {
        "empresas": sorted(result, key=lambda x: x["valor_total"], reverse=True),
    }
