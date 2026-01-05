from typing import List

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
