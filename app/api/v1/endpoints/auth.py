from datetime import timedelta, datetime
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.repositories.pessoa_repository import PessoaRepository
from app.repositories.rota_repository import PontoParadaRepository
from app.schemas.token import Token
from app.schemas.pessoa import PessoaResponse
from app.schemas.auth import RegistroUsuario, SolicitarResetSenha, RedefinirSenha
from app.services.email_service import email_service

router = APIRouter()


@router.post("/registro", response_model=PessoaResponse, status_code=status.HTTP_201_CREATED)
def registro(
    dados: RegistroUsuario,
    db: Session = Depends(get_db),
):
    """
    Registra um novo usuário no sistema.
    
    Rota pública para pessoas se cadastrarem.
    """
    repository = PessoaRepository(db)

    # Verifica se email já existe
    if repository.get_by_email(dados.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado",
        )

    # Verifica se CPF já existe
    if repository.get_by_cpf(dados.cpf):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já cadastrado",
        )

    # Verifica se PIS já existe
    if repository.get_by_pis(dados.pis):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PIS já cadastrado",
        )

    # Verifica se ponto de parada existe (se informado)
    if dados.ponto_parada_id:
        ponto_repo = PontoParadaRepository(db)
        ponto = ponto_repo.get_by_id(dados.ponto_parada_id)
        if not ponto:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ponto de parada não encontrado",
            )

    # Cria o usuário
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Registro payload - Nome: {dados.nome}, CPF: {dados.cpf}, PIS: {dados.pis}")

    if not dados.pis:
        logger.error(f"Tentativa de registro sem PIS! Dados: {dados}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O campo PIS é obrigatório e não foi recebido corretamente."
        )

    from app.schemas.pessoa import PessoaCreate
    pessoa_data = PessoaCreate(
        nome=dados.nome,
        email=dados.email,
        cpf=dados.cpf,
        pis=dados.pis,
        telefone=dados.telefone,
        senha=dados.senha,
        ponto_parada_id=dados.ponto_parada_id,
        foto_url=dados.foto_url,
    )

    nova_pessoa = repository.create(pessoa_data)
    return nova_pessoa


from pydantic import BaseModel as PydanticBaseModel

class FotoRegistroUpload(PydanticBaseModel):
    """Schema para upload de foto durante registro."""
    foto_base64: str
    cpf: str  # Usa CPF como identificador temporário
    content_type: str = "image/jpeg"


from app.services.storage_service import storage_service
import hashlib

@router.post("/upload-foto-registro")
def upload_foto_registro(dados: FotoRegistroUpload):
    """
    Faz upload de foto de perfil durante o registro.
    Rota pública - usa CPF (hasheado) como identificador temporário.
    """
    try:
        # Usa hash do CPF como ID temporário
        cpf_hash = hashlib.md5(dados.cpf.encode()).hexdigest()[:8]
        
        url = storage_service.upload_perfil_foto(
            foto_base64=dados.foto_base64,
            pessoa_id=int(cpf_hash, 16) % 100000,  # Converte para número
            content_type=dados.content_type,
        )
        
        return {"url": url, "message": "Foto enviada com sucesso!"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fazer upload: {str(e)}"
        )


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Realiza login e retorna token de acesso."""
    repository = PessoaRepository(db)
    user = repository.get_by_email(form_data.username)

    if not user or not user.senha_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Inclui perfis do usuário no token
    perfis_data = [
        {
            "id": perfil.id,
            "codigo": perfil.codigo,
            "nome": perfil.nome
        }
        for perfil in user.perfis if perfil.ativo
    ]
    
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "nome": user.nome,
            "tipo_pessoa": user.tipo_pessoa.value,
            "perfis": perfis_data,
        },
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token)


@router.post("/esqueci-senha")
def esqueci_senha(
    dados: SolicitarResetSenha,
    db: Session = Depends(get_db),
):
    """
    Solicita reset de senha.
    Envia email com link e token para redefinir senha.
    """
    repository = PessoaRepository(db)
    user = repository.get_by_email(dados.email)

    # Por segurança, sempre retorna sucesso mesmo se email não existir
    # Isso evita que atacantes descubram emails válidos no sistema
    if not user:
        return {
            "message": "Se o email estiver cadastrado, você receberá as instruções para redefinir sua senha."
        }

    # Gera token seguro de reset
    reset_token = secrets.token_urlsafe(32)
    
    # Define expiração (1 hora)
    expires = datetime.utcnow() + timedelta(hours=1)
    
    # Salva token no banco
    user.reset_token = reset_token
    user.reset_token_expires = expires
    db.commit()

    # Envia email com link de reset
    email_service.enviar_email_reset_senha(
        email=user.email,
        nome=user.nome,
        token=reset_token,
    )

    return {
        "message": "Se o email estiver cadastrado, você receberá as instruções para redefinir sua senha."
    }


@router.post("/redefinir-senha")
def redefinir_senha(
    dados: RedefinirSenha,
    db: Session = Depends(get_db),
):
    """
    Redefine senha usando token recebido por email.
    """
    repository = PessoaRepository(db)
    
    # Busca usuário pelo token
    user = db.query(repository.model).filter(
        repository.model.reset_token == dados.token
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado",
        )

    # Verifica se token expirou
    if not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expirado. Solicite um novo link de recuperação.",
        )

    # Atualiza senha
    user.senha_hash = get_password_hash(dados.nova_senha)
    
    # Limpa token de reset
    user.reset_token = None
    user.reset_token_expires = None
    
    db.commit()

    # Envia email de confirmação
    email_service.enviar_email_confirmacao_reset(
        email=user.email,
        nome=user.nome,
    )

    return {
        "message": "Senha redefinida com sucesso! Você já pode fazer login com sua nova senha."
    }

