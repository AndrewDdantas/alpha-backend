from typing import List, Dict, Any
from datetime import date, timedelta, datetime
import calendar

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.deps import get_db, get_current_user
from app.core.permissions import require_authenticated
from app.models.pessoa import Pessoa
from app.models.diaria import Diaria, Inscricao
from app.models.enums import StatusInscricao, TipoPessoa

router = APIRouter()

def get_fifth_business_day(year: int, month: int) -> date:
    """Calcula o 5º dia útil do mês (considerando apenas seg-sex como útil)."""
    day = 1
    business_days = 0
    while business_days < 5:
        current_date = date(year, month, day)
        # 0 = Segunda, 4 = Sexta, 5 = Sábado, 6 = Domingo
        if current_date.weekday() < 5:
            business_days += 1
        
        if business_days == 5:
            return current_date
        
        day += 1
    return date(year, month, 5) # Fallback seguro

@router.get("/previsao")
def get_previsao_pagamentos(
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_authenticated()),
):
    """
    Retorna previsão de pagamentos baseada nas diárias trabalhadas.
    Regras:
    - Diárias de 1-15: Recebe dia 20 do mesmo mês.
    - Diárias de 16-fim: Recebe 5º dia útil do mês seguinte.
    """
    
    # Busca apenas inscrições concluídas ou confirmadas
    # (Confirmadas entram na previsão, Concluídas já devem ter sido processadas ou são histórico)
    inscricoes = (
        db.query(Inscricao)
        .join(Diaria)
        .filter(
            Inscricao.pessoa_id == current_user.id,
            Inscricao.status.in_([StatusInscricao.CONFIRMADA, StatusInscricao.CONCLUIDA]),
            Diaria.data <= date.today() # Apenas diárias que já aconteceram entram no cálculo de "trabalhado"
            # Se quiser incluir diárias futuras como "previsão futura", remover o filtro de data combinaria melhor com "calendário"
            # O user disse "tudo que ele trabalha", o que implica passado, mas num calendário é legal ver o futuro.
            # Vou remover o filtro de data para mostrar tudo planejado também.
        )
        .order_by(Diaria.data.desc())
        .all()
    )
    
    # Agrupamento
    pagamentos: Dict[str, Dict[str, Any]] = {}
    
    for inscricao in inscricoes:
        diaria = inscricao.diaria
        valor = diaria.valor or 0
        
        # Define o período
        mes = diaria.data.month
        ano = diaria.data.year
        dia = diaria.data.day
        
        if dia <= 15:
            periodo_key = f"{ano}-{mes:02d}-1" # 1ª Quinzena
            data_pagamento = date(ano, mes, 20)
            descricao_periodo = f"1ª Quinzena de {calendar.month_name[mes]}"
        else:
            periodo_key = f"{ano}-{mes:02d}-2" # 2ª Quinzena
            # Calcula mês seguinte
            prox_mes = mes + 1
            prox_ano = ano
            if prox_mes > 12:
                prox_mes = 1
                prox_ano += 1
            
            data_pagamento = get_fifth_business_day(prox_ano, prox_mes)
            descricao_periodo = f"2ª Quinzena de {calendar.month_name[mes]}"
            
        key = f"{data_pagamento.isoformat()}"
        
        if key not in pagamentos:
            pagamentos[key] = {
                "data_pagamento": data_pagamento,
                "periodo_referencia": descricao_periodo, # Ex: "1ª Quinzena de Janeiro" ... teria que traduzir mês, melhor usar numérico no front ou formatar
                "valor_total": 0,
                "qtd_diarias": 0,
                "status": "Previsto" if data_pagamento >= date.today() else "Realizado",
                "detalhes": []
            }
            
        pagamentos[key]["valor_total"] += float(valor)
        pagamentos[key]["qtd_diarias"] += 1
        pagamentos[key]["detalhes"].append({
            "data_diaria": diaria.data,
            "titulo": diaria.titulo,
            "valor": float(valor)
        })

    # Transforma em lista e ordena por data de pagamento (mais recente primeiro)
    lista_pagamentos = sorted(
        pagamentos.values(), 
        key=lambda x: x["data_pagamento"], 
        reverse=True
    )
    
    return lista_pagamentos
