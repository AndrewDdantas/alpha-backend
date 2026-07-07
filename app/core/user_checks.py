"""Validações de status do usuário (ativo/bloqueado)."""

from datetime import date

from fastapi import HTTPException, status

from app.models.pessoa import Pessoa


def is_pessoa_blocked(pessoa: Pessoa) -> bool:
    """Retorna True se o usuário está bloqueado no momento."""
    if not pessoa.bloqueado:
        return False
    if pessoa.bloqueado_ate is None:
        return True
    return pessoa.bloqueado_ate >= date.today()


def get_block_message(pessoa: Pessoa) -> str:
    motivo = pessoa.motivo_bloqueio or "Conta bloqueada"
    if pessoa.bloqueado_ate:
        return (
            f"Conta bloqueada até {pessoa.bloqueado_ate.strftime('%d/%m/%Y')}. "
            f"Motivo: {motivo}"
        )
    return f"Conta bloqueada. Motivo: {motivo}"


def assert_user_active(pessoa: Pessoa) -> None:
    if not pessoa.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )


def assert_user_not_blocked(pessoa: Pessoa) -> None:
    if is_pessoa_blocked(pessoa):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=get_block_message(pessoa),
        )


def assert_user_can_access(pessoa: Pessoa) -> None:
    """Garante que o usuário está ativo e não bloqueado."""
    assert_user_active(pessoa)
    assert_user_not_blocked(pessoa)
