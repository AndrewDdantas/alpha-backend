"""
Script para criar usuário administrador inicial.
Execute: python scripts/create_admin.py
"""
import sys
sys.path.insert(0, '.')

from app.db.session import SessionLocal
from app.models.pessoa import Pessoa
from app.models.enums import TipoPessoa
from app.core.security import get_password_hash


def create_admin():
    """Cria o usuário administrador inicial."""
    db = SessionLocal()
    
    try:
        # Verifica se já existe um admin
        existing_admin = db.query(Pessoa).filter(Pessoa.email == "admin@admin.com").first()
        if existing_admin:
            print("⚠️  Usuário admin já existe!")
            print(f"   Email: {existing_admin.email}")
            return
        
        # Cria o admin
        admin = Pessoa(
            nome="Administrador",
            email="admin@admin.com",
            cpf="00000000000",
            senha_hash=get_password_hash("admin123"),
            tipo_pessoa=TipoPessoa.ADMIN,
            ativo=True,
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("✅ Usuário administrador criado com sucesso!")
        print(f"   Email: admin@admin.com")
        print(f"   Senha: admin123")
        print(f"   Tipo: {admin.tipo_pessoa.value}")
        print("")
        print("⚠️  IMPORTANTE: Altere a senha após o primeiro login!")
        
    except Exception as e:
        print(f"❌ Erro ao criar admin: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
