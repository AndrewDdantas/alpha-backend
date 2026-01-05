from datetime import time
from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.permissions import require_admin
from app.models.pessoa import Pessoa
from app.models.turno import Turno
from app.schemas.empresa import EmpresaCreate, EmpresaUpdate, EmpresaResponse, EmpresaList
from app.schemas.turno import TurnoCreate, TurnoUpdate, TurnoResponse
from app.services.empresa_service import EmpresaService

router = APIRouter()


@router.get("/", response_model=EmpresaList)
def list_empresas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Lista todas as empresas (admin)."""
    service = EmpresaService(db)
    return service.list_empresas(skip=skip, limit=limit)


@router.get("/{empresa_id}", response_model=EmpresaResponse)
def get_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Busca uma empresa por ID (admin)."""
    service = EmpresaService(db)
    return service.get_empresa(empresa_id)


@router.post("/", response_model=EmpresaResponse, status_code=status.HTTP_201_CREATED)
def create_empresa(
    empresa_data: EmpresaCreate,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Cria uma nova empresa (admin)."""
    service = EmpresaService(db)
    return service.create_empresa(empresa_data)


@router.put("/{empresa_id}", response_model=EmpresaResponse)
def update_empresa(
    empresa_id: int,
    empresa_data: EmpresaUpdate,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Atualiza uma empresa (admin)."""
    service = EmpresaService(db)
    return service.update_empresa(empresa_id, empresa_data)


@router.delete("/{empresa_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Remove uma empresa (admin)."""
    service = EmpresaService(db)
    service.delete_empresa(empresa_id)
    return None


# ========== Turnos ==========

def _parse_time(time_str: str) -> time:
    """Converte string HH:MM para time."""
    parts = time_str.split(":")
    return time(int(parts[0]), int(parts[1]))


@router.get("/{empresa_id}/turnos", response_model=List[TurnoResponse])
def list_turnos(
    empresa_id: int,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Lista turnos de uma empresa."""
    service = EmpresaService(db)
    service.get_empresa(empresa_id)  # Verifica se empresa existe
    
    turnos = db.query(Turno).filter(
        Turno.empresa_id == empresa_id,
        Turno.ativo == True
    ).order_by(Turno.hora_inicio).all()
    return turnos


@router.post("/{empresa_id}/turnos", response_model=TurnoResponse, status_code=status.HTTP_201_CREATED)
def create_turno(
    empresa_id: int,
    turno_data: TurnoCreate,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Cria um turno para uma empresa."""
    service = EmpresaService(db)
    service.get_empresa(empresa_id)  # Verifica se empresa existe
    
    turno = Turno(
        empresa_id=empresa_id,
        nome=turno_data.nome,
        hora_inicio=_parse_time(turno_data.hora_inicio),
        hora_fim=_parse_time(turno_data.hora_fim),
    )
    db.add(turno)
    db.commit()
    db.refresh(turno)
    return turno


@router.put("/turnos/{turno_id}", response_model=TurnoResponse)
def update_turno(
    turno_id: int,
    turno_data: TurnoUpdate,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Atualiza um turno."""
    turno = db.query(Turno).filter(Turno.id == turno_id).first()
    if not turno:
        raise HTTPException(status_code=404, detail="Turno não encontrado")
    
    if turno_data.nome is not None:
        turno.nome = turno_data.nome
    if turno_data.hora_inicio is not None:
        turno.hora_inicio = _parse_time(turno_data.hora_inicio)
    if turno_data.hora_fim is not None:
        turno.hora_fim = _parse_time(turno_data.hora_fim)
    if turno_data.ativo is not None:
        turno.ativo = turno_data.ativo
    
    db.commit()
    db.refresh(turno)
    return turno


@router.delete("/turnos/{turno_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_turno(
    turno_id: int,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Remove um turno."""
    turno = db.query(Turno).filter(Turno.id == turno_id).first()
    if not turno:
        raise HTTPException(status_code=404, detail="Turno não encontrado")
    
    db.delete(turno)
    db.commit()
    return None

