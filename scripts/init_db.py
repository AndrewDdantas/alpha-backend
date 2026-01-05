"""
Script para criar todas as tabelas no banco de dados.
Execute: python scripts/init_db.py
"""
import sys
sys.path.insert(0, '.')

from app.db.session import engine
from app.db.base import Base

# Importa todos os models para que sejam registrados
from app.models.pessoa import Pessoa
from app.models.empresa import Empresa
from app.models.diaria import Diaria, Inscricao
from app.models.rota import Rota, PontoParada
from app.models.veiculo import Veiculo
from app.models.alocacao import AlocacaoDiaria, AlocacaoColaborador


def init_db():
    """Cria todas as tabelas no banco de dados."""
    print("🔄 Criando tabelas no banco de dados...")
    
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas com sucesso!")
        print("")
        print("Tabelas:")
        for table in Base.metadata.tables:
            print(f"   - {table}")
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")


if __name__ == "__main__":
    init_db()
