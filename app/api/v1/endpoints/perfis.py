from typing import Optional
from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.permissions import require_admin
from app.models.pessoa import Pessoa
from app.schemas.perfil import (
    PerfilCreate,
    PerfilUpdate,
    PerfilResponse,
    PerfilList,
    PermissaoCreate,
    PermissaoUpdate,
    PermissaoResponse,
    PermissaoList,
    AtribuirPerfil,
    RemoverPerfil,
    UsuarioPerfis,
    PerfilSimples,
)
from app.services.perfil_service import PerfilService

router = APIRouter()


# ========== Endpoints de Perfis ==========

@router.get("/perfis", response_model=PerfilList)
def list_perfis(
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = Query(None),
    sistema: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Lista todos os perfis com filtros."""
    service = PerfilService(db)
    return service.list_perfis(skip=skip, limit=limit, ativo=ativo, sistema=sistema)


@router.get("/perfis/{perfil_id}", response_model=PerfilResponse)
def get_perfil(
    perfil_id: int,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Retorna um perfil específico."""
    service = PerfilService(db)
    return service.get_perfil(perfil_id)


@router.post("/perfis", response_model=PerfilResponse, status_code=status.HTTP_201_CREATED)
def create_perfil(
    perfil_data: PerfilCreate,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Cria um novo perfil."""
    service = PerfilService(db)
    return service.create_perfil(perfil_data)


@router.put("/perfis/{perfil_id}", response_model=PerfilResponse)
def update_perfil(
    perfil_id: int,
    perfil_data: PerfilUpdate,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Atualiza um perfil."""
    service = PerfilService(db)
    return service.update_perfil(perfil_id, perfil_data)


@router.delete("/perfis/{perfil_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_perfil(
    perfil_id: int,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Exclui um perfil (apenas se não for de sistema)."""
    service = PerfilService(db)
    service.delete_perfil(perfil_id)


# ========== Endpoints de Permissões ==========

@router.get("/permissoes", response_model=PermissaoList)
def list_permissoes(
    skip: int = 0,
    limit: int = 1000,
    ativo: Optional[bool] = Query(None),
    recurso: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Lista todas as permissões disponíveis."""
    service = PerfilService(db)
    return service.list_permissoes(skip=skip, limit=limit, ativo=ativo, recurso=recurso)


@router.get("/permissoes/{permissao_id}", response_model=PermissaoResponse)
def get_permissao(
    permissao_id: int,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Retorna uma permissão específica."""
    service = PerfilService(db)
    return service.get_permissao(permissao_id)


@router.post("/permissoes", response_model=PermissaoResponse, status_code=status.HTTP_201_CREATED)
def create_permissao(
    permissao_data: PermissaoCreate,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Cria uma nova permissão."""
    service = PerfilService(db)
    return service.create_permissao(permissao_data)


@router.put("/permissoes/{permissao_id}", response_model=PermissaoResponse)
def update_permissao(
    permissao_id: int,
    permissao_data: PermissaoUpdate,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Atualiza uma permissão."""
    service = PerfilService(db)
    return service.update_permissao(permissao_id, permissao_data)


@router.delete("/permissoes/{permissao_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_permissao(
    permissao_id: int,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Exclui uma permissão."""
    service = PerfilService(db)
    service.delete_permissao(permissao_id)


# ========== Endpoints de Atribuição de Perfis ==========

@router.post("/atribuir-perfil")
def atribuir_perfil(
    dados: AtribuirPerfil,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Atribui um perfil a um usuário."""
    service = PerfilService(db)
    return service.atribuir_perfil_a_pessoa(
        pessoa_id=dados.pessoa_id,
        perfil_id=dados.perfil_id,
        atribuido_por_id=current_user.id,
    )


@router.post("/remover-perfil")
def remover_perfil(
    dados: RemoverPerfil,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Remove um perfil de um usuário."""
    service = PerfilService(db)
    return service.remover_perfil_de_pessoa(
        pessoa_id=dados.pessoa_id,
        perfil_id=dados.perfil_id,
    )


@router.get("/usuarios/{pessoa_id}/perfis")
def get_perfis_usuario(
    pessoa_id: int,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Retorna todos os perfis de um usuário."""
    service = PerfilService(db)
    pessoa = db.query(Pessoa).filter(Pessoa.id == pessoa_id).first()
    if not pessoa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )
    
    perfis = service.get_perfis_da_pessoa(pessoa_id)
    return {
        "pessoa_id": pessoa.id,
        "nome": pessoa.nome,
        "email": pessoa.email,
        "tipo_pessoa": pessoa.tipo_pessoa.value,
        "perfis": perfis,
    }


@router.get("/usuarios/{pessoa_id}/permissoes")
def get_permissoes_usuario(
    pessoa_id: int,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Retorna todas as permissões de um usuário (através dos perfis)."""
    service = PerfilService(db)
    permissoes = service.get_permissoes_da_pessoa(pessoa_id)
    return {"permissoes": permissoes}


@router.get("/usuarios/{pessoa_id}/verificar-permissao/{codigo_permissao}")
def verificar_permissao_usuario(
    pessoa_id: int,
    codigo_permissao: str,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Verifica se um usuário tem uma permissão específica."""
    service = PerfilService(db)
    tem_permissao = service.verificar_permissao(pessoa_id, codigo_permissao)
    return {"tem_permissao": tem_permissao}
