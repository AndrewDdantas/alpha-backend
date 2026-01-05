"""
Script de migração para criar tabela turnos.
Execute com: python scripts/add_turnos.py
"""
import sys
sys.path.insert(0, ".")

from sqlalchemy import text
from app.db.session import engine

def run_migration():
    """Cria tabela turnos."""
    
    sql = """
    CREATE TABLE IF NOT EXISTS turnos (
        id SERIAL PRIMARY KEY,
        empresa_id INTEGER NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
        nome VARCHAR(100) NOT NULL,
        hora_inicio TIME NOT NULL,
        hora_fim TIME NOT NULL,
        ativo BOOLEAN DEFAULT TRUE,
        criado_em TIMESTAMP DEFAULT NOW(),
        atualizado_em TIMESTAMP DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS idx_turnos_empresa ON turnos(empresa_id);
    """
    
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    
    print("✅ Tabela turnos criada com sucesso!")

if __name__ == "__main__":
    run_migration()
