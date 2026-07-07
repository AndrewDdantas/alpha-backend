"""Testes para validações de status do usuário."""

from datetime import date, timedelta

import pytest
from fastapi import HTTPException

from app.core.user_checks import assert_user_not_blocked, is_pessoa_blocked
from app.models.pessoa import Pessoa


def _pessoa(**kwargs) -> Pessoa:
    defaults = {
        "id": 1,
        "nome": "Teste",
        "email": "teste@example.com",
        "cpf": "12345678901",
        "pis": "12345678901",
        "ativo": True,
        "bloqueado": False,
    }
    defaults.update(kwargs)
    return Pessoa(**defaults)


def test_usuario_nao_bloqueado():
    pessoa = _pessoa()
    assert is_pessoa_blocked(pessoa) is False


def test_bloqueio_permanente():
    pessoa = _pessoa(bloqueado=True, bloqueado_ate=None)
    assert is_pessoa_blocked(pessoa) is True

    with pytest.raises(HTTPException) as exc:
        assert_user_not_blocked(pessoa)

    assert exc.value.status_code == 403


def test_bloqueio_temporario_ativo():
    pessoa = _pessoa(
        bloqueado=True,
        bloqueado_ate=date.today() + timedelta(days=1),
        motivo_bloqueio="Falta",
    )
    assert is_pessoa_blocked(pessoa) is True


def test_bloqueio_temporario_expirado():
    pessoa = _pessoa(
        bloqueado=True,
        bloqueado_ate=date.today() - timedelta(days=1),
    )
    assert is_pessoa_blocked(pessoa) is False
