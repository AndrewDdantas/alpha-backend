from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.pessoa import Pessoa
from app.schemas.pessoa import PessoaCreate, PessoaUpdate
from app.core.security import get_password_hash


class PessoaRepository:
    """Repositório para operações CRUD de Pessoa."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, pessoa_id: int) -> Optional[Pessoa]:
        """Busca pessoa por ID."""
        return self.db.query(Pessoa).filter(Pessoa.id == pessoa_id).first()

    def get_by_email(self, email: str) -> Optional[Pessoa]:
        """Busca pessoa por email."""
        return self.db.query(Pessoa).filter(Pessoa.email == email).first()

    def get_by_cpf(self, cpf: str) -> Optional[Pessoa]:
        """Busca pessoa por CPF."""
        return self.db.query(Pessoa).filter(Pessoa.cpf == cpf).first()

    def get_by_pis(self, pis: str) -> Optional[Pessoa]:
        """Busca pessoa por PIS."""
        return self.db.query(Pessoa).filter(Pessoa.pis == pis).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Pessoa]:
        """Lista todas as pessoas com paginação."""
        return self.db.query(Pessoa).offset(skip).limit(limit).all()

    def count(self) -> int:
        """Conta total de pessoas."""
        return self.db.query(Pessoa).count()

    def create(self, pessoa_data: PessoaCreate) -> Pessoa:
        """Cria uma nova pessoa."""
        db_pessoa = Pessoa(
            nome=pessoa_data.nome,
            email=pessoa_data.email,
            cpf=pessoa_data.cpf,
            pis=pessoa_data.pis,
            telefone=pessoa_data.telefone,
            data_nascimento=pessoa_data.data_nascimento,
            endereco=pessoa_data.endereco,
            cidade=pessoa_data.cidade,
            estado=pessoa_data.estado,
            cep=pessoa_data.cep,
            tipo_pessoa=pessoa_data.tipo_pessoa,
            ponto_parada_id=pessoa_data.ponto_parada_id,
        )
        if pessoa_data.senha:
            db_pessoa.senha_hash = get_password_hash(pessoa_data.senha)

        self.db.add(db_pessoa)
        self.db.commit()
        self.db.refresh(db_pessoa)
        return db_pessoa

    def update(self, pessoa_id: int, pessoa_data: PessoaUpdate) -> Optional[Pessoa]:
        """Atualiza uma pessoa existente."""
        db_pessoa = self.get_by_id(pessoa_id)
        if not db_pessoa:
            return None

        update_data = pessoa_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_pessoa, field, value)

        self.db.commit()
        self.db.refresh(db_pessoa)
        return db_pessoa

    def delete(self, pessoa_id: int) -> bool:
        """Remove uma pessoa."""
        db_pessoa = self.get_by_id(pessoa_id)
        if not db_pessoa:
            return False

        self.db.delete(db_pessoa)
        self.db.commit()
        return True
