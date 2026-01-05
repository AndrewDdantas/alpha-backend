from typing import Optional, List
from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.permissions import require_authenticated, require_admin
from app.models.pessoa import Pessoa
from app.models.diaria import Inscricao, Diaria
from app.models.enums import TipoPessoa
from app.schemas.pessoa import PessoaCreate, PessoaUpdate, PessoaResponse, PessoaList, PerfilUpdate, BloquearPessoa
from app.services.pessoa_service import PessoaService

router = APIRouter()


# ========== Endpoints de Perfil do Usuário Logado ==========

@router.get("/me", response_model=PessoaResponse)
def get_meu_perfil(
    current_user: Pessoa = Depends(require_authenticated()),
):
    """Retorna os dados do usuário logado."""
    return current_user


@router.put("/me", response_model=PessoaResponse)
def update_meu_perfil(
    perfil_data: PerfilUpdate,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_authenticated()),
):
    """Atualiza o perfil do usuário logado.
    Apenas telefone, ponto de parada e foto podem ser alterados.
    """
    service = PessoaService(db)
    return service.update_perfil(current_user.id, perfil_data)


from pydantic import BaseModel as PydanticBaseModel

class FotoPerfilUpload(PydanticBaseModel):
    foto_base64: str
    content_type: str = "image/jpeg"


from app.services.storage_service import storage_service

@router.post("/me/upload-foto")
def upload_foto_perfil(
    dados: FotoPerfilUpload,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_authenticated()),
):
    """Faz upload de foto de perfil do usuário logado."""
    try:
        # Upload para Supabase Storage
        url = storage_service.upload_perfil_foto(
            foto_base64=dados.foto_base64,
            pessoa_id=current_user.id,
            content_type=dados.content_type,
        )
        
        # Atualiza foto_url no banco
        current_user.foto_url = url
        db.commit()
        
        return {"url": url, "message": "Foto atualizada com sucesso!"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fazer upload: {str(e)}"
        )


# ========== Endpoints Admin ==========

@router.get("/", response_model=PessoaList)
def list_pessoas(
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[str] = Query(None, description="Filtrar por tipo (colaborador, supervisor, admin)"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status ativo"),
    bloqueado: Optional[bool] = Query(None, description="Filtrar por bloqueio"),
    search: Optional[str] = Query(None, description="Buscar por nome ou email"),
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Lista todas as pessoas cadastradas com filtros."""
    query = db.query(Pessoa)
    
    if tipo:
        query = query.filter(Pessoa.tipo_pessoa == tipo)
    if ativo is not None:
        query = query.filter(Pessoa.ativo == ativo)
    if bloqueado is not None:
        query = query.filter(Pessoa.bloqueado == bloqueado)
    if search:
        query = query.filter(
            (Pessoa.nome.ilike(f"%{search}%")) | 
            (Pessoa.email.ilike(f"%{search}%"))
        )
    
    total = query.count()
    pessoas = query.order_by(Pessoa.nome).offset(skip).limit(limit).all()
    
    return PessoaList(total=total, pessoas=pessoas)


@router.get("/{pessoa_id}", response_model=PessoaResponse)
def get_pessoa(
    pessoa_id: int,
    db: Session = Depends(get_db),
):
    """Busca uma pessoa pelo ID."""
    service = PessoaService(db)
    return service.get_pessoa(pessoa_id)


@router.post("/", response_model=PessoaResponse, status_code=status.HTTP_201_CREATED)
def create_pessoa(
    pessoa_data: PessoaCreate,
    db: Session = Depends(get_db),
):
    """Cria uma nova pessoa."""
    service = PessoaService(db)
    return service.create_pessoa(pessoa_data)


@router.put("/{pessoa_id}", response_model=PessoaResponse)
def update_pessoa(
    pessoa_id: int,
    pessoa_data: PessoaUpdate,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Atualiza uma pessoa existente."""
    service = PessoaService(db)
    return service.update_pessoa(pessoa_id, pessoa_data)


@router.delete("/{pessoa_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pessoa(
    pessoa_id: int,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Remove uma pessoa."""
    service = PessoaService(db)
    service.delete_pessoa(pessoa_id)
    return None


@router.post("/{pessoa_id}/bloquear", response_model=PessoaResponse)
def bloquear_pessoa(
    pessoa_id: int,
    dados: BloquearPessoa,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Bloqueia uma pessoa com motivo."""
    pessoa = db.query(Pessoa).filter(Pessoa.id == pessoa_id).first()
    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    
    pessoa.bloqueado = True
    pessoa.motivo_bloqueio = dados.motivo
    pessoa.bloqueado_ate = dados.bloqueado_ate
    
    db.commit()
    db.refresh(pessoa)
    return pessoa


@router.post("/{pessoa_id}/desbloquear", response_model=PessoaResponse)
def desbloquear_pessoa(
    pessoa_id: int,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Desbloqueia uma pessoa."""
    pessoa = db.query(Pessoa).filter(Pessoa.id == pessoa_id).first()
    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    
    pessoa.bloqueado = False
    pessoa.motivo_bloqueio = None
    pessoa.bloqueado_ate = None
    
    db.commit()
    db.refresh(pessoa)
    return pessoa


@router.get("/{pessoa_id}/diarias")
def listar_diarias_pessoa(
    pessoa_id: int,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Lista todas as diárias de uma pessoa."""
    pessoa = db.query(Pessoa).filter(Pessoa.id == pessoa_id).first()
    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    
    inscricoes = db.query(Inscricao).filter(
        Inscricao.pessoa_id == pessoa_id
    ).order_by(Inscricao.criado_em.desc()).all()
    
    result = []
    for inscricao in inscricoes:
        diaria = inscricao.diaria
        result.append({
            "inscricao_id": inscricao.id,
            "status_inscricao": inscricao.status.value,
            "diaria_id": diaria.id,
            "titulo": diaria.titulo,
            "data": str(diaria.data),
            "empresa": diaria.empresa.nome,
            "status_diaria": diaria.status.value,
            "valor": float(diaria.valor) if diaria.valor else None,
        })
    
    return {
        "pessoa_id": pessoa_id,
        "nome": pessoa.nome,
        "total_diarias": len(result),
        "diarias": result,
    }


