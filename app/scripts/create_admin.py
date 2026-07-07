"""Cria a conta admin inicial a partir do .env."""

import os
from typing import Optional

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.enums import TipoPessoa
from app.models.pessoa import Pessoa


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value or not value.strip():
        raise RuntimeError(f"Variavel obrigatoria ausente no .env: {name}")
    return value.strip()


def _optional_env(name: str) -> Optional[str]:
    value = os.getenv(name)
    if not value or not value.strip():
        return None
    return value.strip()


def main() -> None:
    email = _required_env("MASTER_ADMIN_EMAIL")
    password = _required_env("MASTER_ADMIN_PASSWORD")
    name = _required_env("MASTER_ADMIN_NAME")
    cpf = _required_env("MASTER_ADMIN_CPF")
    pis = _required_env("MASTER_ADMIN_PIS")
    phone = _optional_env("MASTER_ADMIN_PHONE")

    db = SessionLocal()
    try:
        admin = db.query(Pessoa).filter(Pessoa.email == email).first()

        if admin:
            if admin.tipo_pessoa != TipoPessoa.ADMIN:
                admin.tipo_pessoa = TipoPessoa.ADMIN
            if not admin.ativo:
                admin.ativo = True
            db.commit()
            print(f"Conta admin ja existe: {email} (senha nao alterada)")
            return

        admin = Pessoa(
            nome=name,
            email=email,
            cpf=cpf,
            pis=pis,
            telefone=phone,
            tipo_pessoa=TipoPessoa.ADMIN,
            ativo=True,
            senha_hash=get_password_hash(password),
        )
        db.add(admin)
        db.commit()
        print(f"Conta admin criada: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
