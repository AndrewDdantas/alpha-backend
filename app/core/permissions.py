from typing import List, Optional

from fastapi import Depends, HTTPException, status

from app.core.deps import get_current_user
from app.models.pessoa import Pessoa
from app.models.enums import TipoPessoa


def require_roles(allowed_roles: List[TipoPessoa]):
    """
    Dependency factory para verificar se o usuário tem permissão.
    
    Uso:
        @router.get("/admin-only")
        def admin_route(user: Pessoa = Depends(require_roles([TipoPessoa.ADMIN]))):
            ...
    """
    async def role_checker(current_user: Pessoa = Depends(get_current_user)) -> Pessoa:
        # Compara o valor do enum (string) para compatibilidade
        user_role = current_user.tipo_pessoa.value if hasattr(current_user.tipo_pessoa, 'value') else current_user.tipo_pessoa
        allowed_values = [r.value for r in allowed_roles]
        
        if user_role not in allowed_values:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar este recurso",
            )
        return current_user
    return role_checker


def require_permission(permission_code: str):
    """
    Dependency factory para verificar se o usuário tem uma permissão específica.
    
    Verifica se o usuário possui a permissão através de seus perfis atribuídos.
    
    Uso:
        @router.post("/criar-diaria")
        def criar_diaria(user: Pessoa = Depends(require_permission("diarias.create"))):
            ...
    """
    async def permission_checker(current_user: Pessoa = Depends(get_current_user)) -> Pessoa:
        # Admin sempre tem todas as permissões
        user_role = current_user.tipo_pessoa.value if hasattr(current_user.tipo_pessoa, 'value') else current_user.tipo_pessoa
        if user_role == TipoPessoa.ADMIN.value:
            return current_user
        
        # Verifica se o usuário tem a permissão através dos perfis
        tem_permissao = False
        for perfil in current_user.perfis:
            if perfil.ativo:
                for permissao in perfil.permissoes:
                    if permissao.ativo and permissao.codigo == permission_code:
                        tem_permissao = True
                        break
            if tem_permissao:
                break
        
        if not tem_permissao:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Você não tem a permissão '{permission_code}' necessária para acessar este recurso",
            )
        
        return current_user
    return permission_checker


def require_any_permission(permission_codes: List[str]):
    """
    Dependency factory para verificar se o usuário tem pelo menos uma das permissões.
    
    Uso:
        @router.get("/relatorios")
        def relatorios(user: Pessoa = Depends(require_any_permission(["relatorios.read", "relatorios.manage"]))):
            ...
    """
    async def permission_checker(current_user: Pessoa = Depends(get_current_user)) -> Pessoa:
        # Admin sempre tem todas as permissões
        user_role = current_user.tipo_pessoa.value if hasattr(current_user.tipo_pessoa, 'value') else current_user.tipo_pessoa
        if user_role == TipoPessoa.ADMIN.value:
            return current_user
        
        # Verifica se o usuário tem pelo menos uma das permissões
        tem_permissao = False
        for perfil in current_user.perfis:
            if perfil.ativo:
                for permissao in perfil.permissoes:
                    if permissao.ativo and permissao.codigo in permission_codes:
                        tem_permissao = True
                        break
            if tem_permissao:
                break
        
        if not tem_permissao:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Você precisa de uma das permissões {permission_codes} para acessar este recurso",
            )
        
        return current_user
    return permission_checker


# Atalhos para verificação de permissões
def require_admin():
    """Requer que o usuário seja admin."""
    return require_roles([TipoPessoa.ADMIN])


def require_supervisor_or_above():
    """Requer que o usuário seja supervisor ou admin."""
    return require_roles([TipoPessoa.SUPERVISOR, TipoPessoa.ADMIN])


def require_authenticated():
    """Requer apenas que o usuário esteja autenticado (qualquer tipo)."""
    return require_roles([TipoPessoa.COLABORADOR, TipoPessoa.SUPERVISOR, TipoPessoa.ADMIN])
