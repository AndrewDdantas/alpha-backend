from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.core.permissions import require_admin, require_authenticated
from app.models.pessoa import Pessoa
from app.models.enums import StatusDiaria, StatusInscricao
from app.schemas.diaria import (
    DiariaCreate, DiariaUpdate, DiariaResponse, DiariaList, DiariaComInscricoes,
    InscricaoCreate, InscricaoResponse, InscricaoComPessoa, MinhaInscricao,
)
from app.services.diaria_service import DiariaService, InscricaoService

router = APIRouter()


# ========== Rotas raiz e estáticas ==========

@router.get("/", response_model=DiariaList)
def list_diarias(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[StatusDiaria] = None,
    empresa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Lista todas as diárias com filtros (admin)."""
    service = DiariaService(db)
    return service.list_diarias(skip=skip, limit=limit, status=status_filter, empresa_id=empresa_id)


@router.post("/", response_model=DiariaResponse, status_code=status.HTTP_201_CREATED)
def create_diaria(
    diaria_data: DiariaCreate,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Cria uma nova diária (admin)."""
    service = DiariaService(db)
    return service.create_diaria(diaria_data)


@router.get("/disponiveis", response_model=DiariaList)
def list_disponiveis(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Lista diárias disponíveis para inscrição (público)."""
    service = DiariaService(db)
    return service.list_disponiveis(skip=skip, limit=limit)


@router.get("/minhas-inscricoes", response_model=List[MinhaInscricao])
def minhas_inscricoes(
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_authenticated()),
):
    """Lista minhas inscrições em diárias."""
    service = InscricaoService(db)
    return service.minhas_inscricoes(current_user.id)


@router.post("/inscrever", response_model=InscricaoResponse, status_code=status.HTTP_201_CREATED)
def inscrever(
    inscricao_data: InscricaoCreate,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_authenticated()),
):
    """Inscreve-se em uma diária."""
    service = InscricaoService(db)
    return service.inscrever(current_user.id, inscricao_data)


# ========== Rotas /inscricoes/* (DEVEM VIR ANTES de /{diaria_id}) ==========

@router.post("/inscricoes/{inscricao_id}/cancelar", response_model=InscricaoResponse)
def cancelar_inscricao(
    inscricao_id: int,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_authenticated()),
):
    """Cancela minha inscrição em uma diária."""
    service = InscricaoService(db)
    return service.cancelar_inscricao(current_user.id, inscricao_id)


@router.put("/inscricoes/{inscricao_id}/status", response_model=InscricaoResponse)
def atualizar_status_inscricao(
    inscricao_id: int,
    novo_status: StatusInscricao,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Atualiza status de uma inscrição (admin)."""
    service = InscricaoService(db)
    return service.atualizar_status(inscricao_id, novo_status)


# ========== Rotas com /{diaria_id} (DEVEM VIR POR ÚLTIMO) ==========

@router.get("/{diaria_id}", response_model=DiariaComInscricoes)
def get_diaria(
    diaria_id: int,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Busca diária com lista de inscritos (admin)."""
    service = DiariaService(db)
    return service.get_diaria_com_inscricoes(diaria_id)


@router.put("/{diaria_id}", response_model=DiariaResponse)
def update_diaria(
    diaria_id: int,
    diaria_data: DiariaUpdate,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Atualiza uma diária (admin)."""
    service = DiariaService(db)
    return service.update_diaria(diaria_id, diaria_data)


@router.delete("/{diaria_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_diaria(
    diaria_id: int,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Remove uma diária (admin)."""
    service = DiariaService(db)
    service.delete_diaria(diaria_id)
    return None


@router.get("/{diaria_id}/inscricoes", response_model=List[InscricaoComPessoa])
def listar_inscritos(
    diaria_id: int,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_authenticated()),
):
    """Lista inscritos de uma diária (admin ou supervisor)."""
    from app.models.diaria import Diaria
    from fastapi import HTTPException
    
    diaria = db.query(Diaria).filter(Diaria.id == diaria_id).first()
    if not diaria:
        raise HTTPException(status_code=404, detail="Diária não encontrada")
    
    # Permite admin, supervisor global ou supervisor da diária
    is_admin = current_user.tipo_pessoa.value in ['admin', 'supervisor']
    is_supervisor_diaria = diaria.supervisor_id == current_user.id
    
    if not is_admin and not is_supervisor_diaria:
        raise HTTPException(status_code=403, detail="Sem permissão para acessar esta diária")
    
    service = InscricaoService(db)
    return service.listar_inscritos(diaria_id)
