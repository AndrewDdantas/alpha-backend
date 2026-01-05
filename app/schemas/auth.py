from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class RegistroUsuario(BaseModel):
    """Schema para registro de novo usuário."""

    nome: str
    email: EmailStr
    cpf: str
    telefone: Optional[str] = None
    senha: str
    ponto_parada_id: Optional[int] = None  # Ponto de embarque do fretado
    foto_url: Optional[str] = None  # URL da foto de perfil (após upload)

    @field_validator("nome")
    @classmethod
    def nome_nao_vazio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Nome é obrigatório")
        return v.strip()

    @field_validator("cpf")
    @classmethod
    def cpf_valido(cls, v: str) -> str:
        # Remove caracteres não numéricos
        cpf = "".join(c for c in v if c.isdigit())
        if len(cpf) != 11:
            raise ValueError("CPF deve ter 11 dígitos")
        return cpf

    @field_validator("senha")
    @classmethod
    def senha_forte(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Senha deve ter no mínimo 6 caracteres")
        return v
