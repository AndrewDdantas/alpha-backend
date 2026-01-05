from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.permissions import require_admin
from app.models.pessoa import Pessoa
from app.schemas.veiculo import VeiculoCreate, VeiculoUpdate, VeiculoResponse, VeiculoList
from app.services.veiculo_service import VeiculoService

router = APIRouter()


@router.get("/", response_model=VeiculoList)
def list_veiculos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Lista todos os veículos ativos."""
    service = VeiculoService(db)
    return service.list_veiculos(skip=skip, limit=limit)


@router.get("/capacidade")
def get_capacidade_total(
    db: Session = Depends(get_db),
):
    """Retorna a capacidade total da frota."""
    service = VeiculoService(db)
    capacidade = service.get_capacidade_total()
    return {"capacidade_total": capacidade}


@router.get("/calcular/{num_passageiros}")
def calcular_veiculos(
    num_passageiros: int,
    db: Session = Depends(get_db),
):
    """
    Calcula quantos veículos são necessários para X passageiros.
    Retorna sugestão de alocação otimizada.
    """
    service = VeiculoService(db)
    return service.calcular_veiculos_necessarios(num_passageiros)


@router.get("/{veiculo_id}/alocacoes")
def listar_alocacoes_veiculo(
    veiculo_id: int,
    db: Session = Depends(get_db),
):
    """Lista todas as diárias em que o veículo foi/está alocado."""
    from app.models.alocacao import AlocacaoDiaria
    from app.models.diaria import Diaria
    
    alocacoes = (
        db.query(AlocacaoDiaria)
        .join(Diaria, AlocacaoDiaria.diaria_id == Diaria.id)
        .filter(AlocacaoDiaria.veiculo_id == veiculo_id)
        .order_by(Diaria.data.desc())
        .all()
    )
    
    result = []
    for aloc in alocacoes:
        diaria = aloc.diaria
        result.append({
            "alocacao_id": aloc.id,
            "diaria_id": diaria.id,
            "diaria_titulo": diaria.titulo,
            "diaria_data": str(diaria.data),
            "diaria_status": diaria.status.value,
            "horario_saida": str(aloc.horario_saida) if aloc.horario_saida else None,
            "empresa": diaria.empresa.nome if diaria.empresa else None,
            "total_colaboradores": len(aloc.colaboradores),
        })
    
    return {
        "veiculo_id": veiculo_id,
        "total_alocacoes": len(result),
        "alocacoes": result,
    }



@router.get("/{veiculo_id}", response_model=VeiculoResponse)
def get_veiculo(
    veiculo_id: int,
    db: Session = Depends(get_db),
):
    """Busca um veículo por ID."""
    service = VeiculoService(db)
    return service.get_veiculo(veiculo_id)


@router.post("/", response_model=VeiculoResponse, status_code=status.HTTP_201_CREATED)
def create_veiculo(
    veiculo_data: VeiculoCreate,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Cria um novo veículo (apenas admin)."""
    service = VeiculoService(db)
    return service.create_veiculo(veiculo_data)


@router.put("/{veiculo_id}", response_model=VeiculoResponse)
def update_veiculo(
    veiculo_id: int,
    veiculo_data: VeiculoUpdate,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Atualiza um veículo (apenas admin)."""
    service = VeiculoService(db)
    return service.update_veiculo(veiculo_id, veiculo_data)


@router.delete("/{veiculo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_veiculo(
    veiculo_id: int,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Remove um veículo (apenas admin)."""
    service = VeiculoService(db)
    service.delete_veiculo(veiculo_id)
    return None
