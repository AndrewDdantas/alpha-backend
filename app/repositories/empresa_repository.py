from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.empresa import Empresa
from app.schemas.empresa import EmpresaCreate, EmpresaUpdate


class EmpresaRepository:
    """Repositório para operações CRUD de Empresa."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, empresa_id: int) -> Optional[Empresa]:
        """Busca empresa por ID."""
        return self.db.query(Empresa).filter(Empresa.id == empresa_id).first()

    def get_by_cnpj(self, cnpj: str) -> Optional[Empresa]:
        """Busca empresa por CNPJ."""
        return self.db.query(Empresa).filter(Empresa.cnpj == cnpj).first()

    def get_all(self, skip: int = 0, limit: int = 100, apenas_ativas: bool = True) -> List[Empresa]:
        """Lista todas as empresas com paginação."""
        query = self.db.query(Empresa)
        if apenas_ativas:
            query = query.filter(Empresa.ativo == True)
        return query.offset(skip).limit(limit).all()

    def count(self, apenas_ativas: bool = True) -> int:
        """Conta total de empresas."""
        query = self.db.query(Empresa)
        if apenas_ativas:
            query = query.filter(Empresa.ativo == True)
        return query.count()

    def create(self, empresa_data: EmpresaCreate) -> Empresa:
        """Cria uma nova empresa."""
        db_empresa = Empresa(
            nome=empresa_data.nome,
            cnpj=empresa_data.cnpj,
            razao_social=empresa_data.razao_social,
            email=empresa_data.email,
            telefone=empresa_data.telefone,
            endereco=empresa_data.endereco,
            cidade=empresa_data.cidade,
            estado=empresa_data.estado,
            cep=empresa_data.cep,
            contato_nome=empresa_data.contato_nome,
            contato_telefone=empresa_data.contato_telefone,
        )
        self.db.add(db_empresa)
        self.db.commit()
        self.db.refresh(db_empresa)
        return db_empresa

    def update(self, empresa_id: int, empresa_data: EmpresaUpdate) -> Optional[Empresa]:
        """Atualiza uma empresa existente."""
        db_empresa = self.get_by_id(empresa_id)
        if not db_empresa:
            return None

        update_data = empresa_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_empresa, field, value)

        self.db.commit()
        self.db.refresh(db_empresa)
        return db_empresa

    def delete(self, empresa_id: int) -> bool:
        """Remove uma empresa."""
        db_empresa = self.get_by_id(empresa_id)
        if not db_empresa:
            return False

        self.db.delete(db_empresa)
        self.db.commit()
        return True
