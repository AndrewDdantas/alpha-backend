"""Endpoints para Registro de Presença."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.deps import get_db
from app.core.permissions import require_authenticated, require_admin, user_is_admin_or_supervisor
from app.models.pessoa import Pessoa
from app.models.diaria import Diaria, Inscricao
from app.models.presenca import RegistroPresenca
from app.schemas.presenca import (
    RegistroPresencaCreate,
    RegistroPresencaResponse,
    PresencaDiariaResponse,
)
from app.services.storage_service import storage_service

router = APIRouter()


# ========== Schema para Upload ==========
class FotoUploadRequest(BaseModel):
    """Schema para upload de foto."""
    foto_base64: str  # Base64 da imagem
    diaria_id: int
    pessoa_id: int
    content_type: str = "image/jpeg"


class FotoUploadResponse(BaseModel):
    """Resposta do upload de foto."""
    url: str
    message: str


# ========== Upload de Foto ==========

@router.post("/upload-foto", response_model=FotoUploadResponse)
def upload_foto_presenca(
    dados: FotoUploadRequest,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_authenticated()),
):
    """Faz upload de foto de presença para o Supabase Storage."""
    
    # Verifica permissão (admin ou supervisor)
    if not user_is_admin_or_supervisor(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas supervisores podem fazer upload de fotos"
        )
    
    try:
        # Faz upload para o Supabase Storage
        url = storage_service.upload_presenca_foto(
            foto_base64=dados.foto_base64,
            diaria_id=dados.diaria_id,
            pessoa_id=dados.pessoa_id,
            content_type=dados.content_type,
        )
        
        return FotoUploadResponse(
            url=url,
            message="Foto enviada com sucesso!"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fazer upload: {str(e)}"
        )


# ========== Supervisor - Registrar Presença ==========

@router.post("/registrar", response_model=RegistroPresencaResponse, status_code=status.HTTP_201_CREATED)
def registrar_presenca(
    presenca_data: RegistroPresencaCreate,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_authenticated()),
):
    """Supervisor registra presença de um colaborador com foto."""
    
    # Busca a inscrição
    inscricao = db.query(Inscricao).filter(Inscricao.id == presenca_data.inscricao_id).first()
    if not inscricao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inscrição não encontrada"
        )
    
    # Verifica se o usuário é o supervisor da diária ou admin
    diaria = inscricao.diaria
    is_admin_supervisor = user_is_admin_or_supervisor(current_user)
    is_diaria_supervisor = diaria.supervisor_id == current_user.id
    
    if not is_admin_supervisor and not is_diaria_supervisor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o supervisor da diária pode registrar presenças"
        )
    
    # Verifica se já existe registro de presença
    existing = db.query(RegistroPresenca).filter(
        RegistroPresenca.inscricao_id == presenca_data.inscricao_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Presença já registrada para esta inscrição"
        )
    
    # Cria o registro
    registro = RegistroPresenca(
        foto_url=presenca_data.foto_url,
        latitude=presenca_data.latitude,
        longitude=presenca_data.longitude,
        observacao=presenca_data.observacao,
        inscricao_id=presenca_data.inscricao_id,
        registrado_por_id=current_user.id,
    )
    
    db.add(registro)
    db.commit()
    db.refresh(registro)
    
    return RegistroPresencaResponse(
        id=registro.id,
        foto_url=registro.foto_url,
        latitude=registro.latitude,
        longitude=registro.longitude,
        observacao=registro.observacao,
        inscricao_id=registro.inscricao_id,
        registrado_por_id=registro.registrado_por_id,
        horario_registro=registro.horario_registro,
        criado_em=registro.criado_em,
        pessoa_nome=inscricao.pessoa.nome,
        pessoa_id=inscricao.pessoa_id,
    )


@router.get("/diaria/{diaria_id}", response_model=PresencaDiariaResponse)
def listar_presencas_diaria(
    diaria_id: int,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_authenticated()),
):
    """Lista todas as presenças de uma diária (supervisor ou admin)."""
    
    diaria = db.query(Diaria).filter(Diaria.id == diaria_id).first()
    if not diaria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diária não encontrada"
        )
    
    # Verifica permissão
    is_admin_supervisor = user_is_admin_or_supervisor(current_user)
    is_diaria_supervisor = diaria.supervisor_id == current_user.id
    
    if not is_admin_supervisor and not is_diaria_supervisor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para ver presenças desta diária"
        )
    
    # Busca inscrições confirmadas
    inscricoes = db.query(Inscricao).filter(
        Inscricao.diaria_id == diaria_id,
        Inscricao.status.in_(['confirmada', 'pendente'])
    ).all()
    
    # Monta lista de inscritos com status de presença
    from app.schemas.presenca import InscritoPresenca
    
    inscritos = []
    presencas = []
    
    for inscricao in inscricoes:
        registro = db.query(RegistroPresenca).filter(
            RegistroPresenca.inscricao_id == inscricao.id
        ).first()
        
        # Adiciona à lista de inscritos
        inscritos.append(InscritoPresenca(
            inscricao_id=inscricao.id,
            pessoa_id=inscricao.pessoa_id,
            pessoa_nome=inscricao.pessoa.nome if inscricao.pessoa else "N/A",
            pessoa_telefone=inscricao.pessoa.telefone if inscricao.pessoa else None,
            status_inscricao=inscricao.status.value,
            presenca_registrada=registro is not None,
            horario_registro=registro.horario_registro if registro else None,
            foto_url=registro.foto_url if registro else None,
        ))
        
        # Se tem registro, adiciona à lista de presenças (retrocompat)
        if registro:
            presencas.append(RegistroPresencaResponse(
                id=registro.id,
                foto_url=registro.foto_url,
                latitude=registro.latitude,
                longitude=registro.longitude,
                observacao=registro.observacao,
                inscricao_id=registro.inscricao_id,
                registrado_por_id=registro.registrado_por_id,
                horario_registro=registro.horario_registro,
                criado_em=registro.criado_em,
                pessoa_nome=inscricao.pessoa.nome,
                pessoa_id=inscricao.pessoa_id,
            ))
    
    return PresencaDiariaResponse(
        diaria_id=diaria.id,
        diaria_titulo=diaria.titulo,
        diaria_local=diaria.local,
        diaria_data=diaria.data.isoformat() if diaria.data else None,
        total_inscritos=len(inscricoes),
        total_presentes=len(presencas),
        inscritos=inscritos,
        presencas=presencas,
    )


@router.get("/minhas-diarias", response_model=List[dict])
def minhas_diarias_supervisor(
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_authenticated()),
):
    """Lista diárias onde o usuário é supervisor."""
    
    diarias = db.query(Diaria).filter(
        Diaria.supervisor_id == current_user.id
    ).order_by(Diaria.data.desc()).all()
    
    result = []
    for diaria in diarias:
        inscricoes_confirmadas = [i for i in diaria.inscricoes if i.status.value in ['confirmada', 'pendente']]
        presencas_registradas = db.query(RegistroPresenca).join(Inscricao).filter(
            Inscricao.diaria_id == diaria.id
        ).count()
        
        result.append({
            "id": diaria.id,
            "titulo": diaria.titulo,
            "data": str(diaria.data),
            "horario_inicio": str(diaria.horario_inicio) if diaria.horario_inicio else None,
            "local": diaria.local,
            "status": diaria.status.value,
            "total_inscritos": len(inscricoes_confirmadas),
            "total_presentes": presencas_registradas,
            "empresa_nome": diaria.empresa.nome,
        })
    
    return result
