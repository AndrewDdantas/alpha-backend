from typing import List, Optional

from fastapi import Depends, HTTPException, status

from app.core.deps import get_current_user
from app.models.pessoa import Pessoa
from app.models.enums import TipoPessoa


def require_roles(allowed_roles: List[TipoPessoa]):
    """
    Dependency factory para verificar se o usuário tem permissão.
    Prioriza verificação por perfis, com fallback para tipo_pessoa.
    
    Uso:
        @router.get("/admin-only")
        def admin_route(user: Pessoa = Depends(require_roles([TipoPessoa.ADMIN]))):
            ...
    """
    async def role_checker(current_user: Pessoa = Depends(get_current_user)) -> Pessoa:
        # Mapeia tipos de pessoa para códigos de perfil
        perfil_map = {
            TipoPessoa.ADMIN: 'ADMINISTRADOR',
            TipoPessoa.SUPERVISOR: ['SUPERVISOR', 'GESTOR_OPERACIONAL', 'ADMINISTRADOR'],
            TipoPessoa.COLABORADOR: ['COLABORADOR', 'SUPERVISOR', 'GESTOR_OPERACIONAL', 'ADMINISTRADOR']
        }
        
        # Verifica por perfis primeiro
        tem_permissao = False
        for role in allowed_roles:
            codigos_perfil = perfil_map.get(role, [])
            if isinstance(codigos_perfil, str):
                codigos_perfil = [codigos_perfil]
            
            for codigo in codigos_perfil:
                if user_has_perfil(current_user, codigo):
                    tem_permissao = True
                    break
            if tem_permissao:
                break
        
        # Fallback para tipo_pessoa se não encontrou perfil
        if not tem_permissao:
            user_role = current_user.tipo_pessoa.value if hasattr(current_user.tipo_pessoa, 'value') else current_user.tipo_pessoa
            allowed_values = [r.value for r in allowed_roles]
            
            if user_role in allowed_values:
                tem_permissao = True
        
        if not tem_permissao:
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


# ========== Funções Helper para Verificação de Perfis/Permissões ==========

def user_has_perfil(user: Pessoa, codigo_perfil: str) -> bool:
    """Verifica se usuário tem um perfil específico (por código)."""
    for perfil in user.perfis:
        if perfil.ativo and perfil.codigo.lower() == codigo_perfil.lower():
            return True
    return False


def user_has_permission(user: Pessoa, codigo_permissao: str) -> bool:
    """Verifica se usuário tem uma permissão específica através de seus perfis."""
    # Admin sempre tem todas as permissões (fallback para tipo_pessoa)
    user_role = user.tipo_pessoa.value if hasattr(user.tipo_pessoa, 'value') else user.tipo_pessoa
    if user_role == TipoPessoa.ADMIN.value:
        return True
    
    # Verifica através dos perfis
    for perfil in user.perfis:
        if perfil.ativo:
            for permissao in perfil.permissoes:
                if permissao.ativo and permissao.codigo == codigo_permissao:
                    return True
    return False


def user_has_any_permission(user: Pessoa, codigos_permissoes: List[str]) -> bool:
    """Verifica se usuário tem pelo menos uma das permissões."""
    return any(user_has_permission(user, codigo) for codigo in codigos_permissoes)


def user_is_admin_or_supervisor(user: Pessoa) -> bool:
    """
    Verifica se usuário é admin ou supervisor.
    Prioriza verificação por perfil, com fallback para tipo_pessoa.
    """
    # Verifica por perfis
    if user_has_perfil(user, 'ADMINISTRADOR') or user_has_perfil(user, 'GESTOR_OPERACIONAL') or user_has_perfil(user, 'SUPERVISOR'):
        return True
    
    # Fallback para tipo_pessoa
    user_role = user.tipo_pessoa.value if hasattr(user.tipo_pessoa, 'value') else user.tipo_pessoa
    return user_role in ['admin', 'supervisor']


# ========== Atalhos para verificação de permissões ==========

def require_admin():
    """Requer que o usuário seja admin."""
    return require_roles([TipoPessoa.ADMIN])


def require_supervisor_or_above():
    """Requer que o usuário seja supervisor ou admin."""
    return require_roles([TipoPessoa.SUPERVISOR, TipoPessoa.ADMIN])


def require_authenticated():
    """Requer apenas que o usuário esteja autenticado (qualquer tipo)."""
    return require_roles([TipoPessoa.COLABORADOR, TipoPessoa.SUPERVISOR, TipoPessoa.ADMIN])
