"""
Script para criar permissões e perfis padrão do sistema.

Execução:
    python -m scripts.seed_perfis
"""
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.perfil import Perfil, Permissao
from app.repositories.perfil_repository import PerfilRepository


# ========== Definição de Permissões por Recurso ==========

PERMISSOES = [
    # Diárias
    {"codigo": "diarias.read", "nome": "Visualizar Diárias", "recurso": "diarias", "acao": "read"},
    {"codigo": "diarias.create", "nome": "Criar Diárias", "recurso": "diarias", "acao": "create"},
    {"codigo": "diarias.update", "nome": "Atualizar Diárias", "recurso": "diarias", "acao": "update"},
    {"codigo": "diarias.delete", "nome": "Excluir Diárias", "recurso": "diarias", "acao": "delete"},
    {"codigo": "diarias.manage", "nome": "Gerenciar Diárias", "recurso": "diarias", "acao": "manage"},
    {"codigo": "diarias.inscrever", "nome": "Inscrever em Diárias", "recurso": "diarias", "acao": "inscrever"},
    
    # Pessoas/Usuários
    {"codigo": "usuarios.read", "nome": "Visualizar Usuários", "recurso": "usuarios", "acao": "read"},
    {"codigo": "usuarios.create", "nome": "Criar Usuários", "recurso": "usuarios", "acao": "create"},
    {"codigo": "usuarios.update", "nome": "Atualizar Usuários", "recurso": "usuarios", "acao": "update"},
    {"codigo": "usuarios.delete", "nome": "Excluir Usuários", "recurso": "usuarios", "acao": "delete"},
    {"codigo": "usuarios.bloquear", "nome": "Bloquear Usuários", "recurso": "usuarios", "acao": "bloquear"},
    
    # Veículos
    {"codigo": "veiculos.read", "nome": "Visualizar Veículos", "recurso": "veiculos", "acao": "read"},
    {"codigo": "veiculos.create", "nome": "Criar Veículos", "recurso": "veiculos", "acao": "create"},
    {"codigo": "veiculos.update", "nome": "Atualizar Veículos", "recurso": "veiculos", "acao": "update"},
    {"codigo": "veiculos.delete", "nome": "Excluir Veículos", "recurso": "veiculos", "acao": "delete"},
    
    # Rotas
    {"codigo": "rotas.read", "nome": "Visualizar Rotas", "recurso": "rotas", "acao": "read"},
    {"codigo": "rotas.create", "nome": "Criar Rotas", "recurso": "rotas", "acao": "create"},
    {"codigo": "rotas.update", "nome": "Atualizar Rotas", "recurso": "rotas", "acao": "update"},
    {"codigo": "rotas.delete", "nome": "Excluir Rotas", "recurso": "rotas", "acao": "delete"},
    
    # Empresas
    {"codigo": "empresas.read", "nome": "Visualizar Empresas", "recurso": "empresas", "acao": "read"},
    {"codigo": "empresas.create", "nome": "Criar Empresas", "recurso": "empresas", "acao": "create"},
    {"codigo": "empresas.update", "nome": "Atualizar Empresas", "recurso": "empresas", "acao": "update"},
    {"codigo": "empresas.delete", "nome": "Excluir Empresas", "recurso": "empresas", "acao": "delete"},
    
    # Alocações
    {"codigo": "alocacoes.read", "nome": "Visualizar Alocações", "recurso": "alocacoes", "acao": "read"},
    {"codigo": "alocacoes.create", "nome": "Criar Alocações", "recurso": "alocacoes", "acao": "create"},
    {"codigo": "alocacoes.update", "nome": "Atualizar Alocações", "recurso": "alocacoes", "acao": "update"},
    {"codigo": "alocacoes.delete", "nome": "Excluir Alocações", "recurso": "alocacoes", "acao": "delete"},
    
    # Presenças
    {"codigo": "presencas.read", "nome": "Visualizar Presenças", "recurso": "presencas", "acao": "read"},
    {"codigo": "presencas.marcar", "nome": "Marcar Presenças", "recurso": "presencas", "acao": "marcar"},
    {"codigo": "presencas.validar", "nome": "Validar Presenças", "recurso": "presencas", "acao": "validar"},
    
    # Relatórios
    {"codigo": "relatorios.read", "nome": "Visualizar Relatórios", "recurso": "relatorios", "acao": "read"},
    {"codigo": "relatorios.export", "nome": "Exportar Relatórios", "recurso": "relatorios", "acao": "export"},
    {"codigo": "relatorios.gestao", "nome": "Relatórios de Gestão", "recurso": "relatorios", "acao": "gestao"},
    
    # Dashboard
    {"codigo": "dashboard.read", "nome": "Visualizar Dashboard", "recurso": "dashboard", "acao": "read"},
    {"codigo": "dashboard.executivo", "nome": "Dashboard Executivo", "recurso": "dashboard", "acao": "executivo"},
    
    # Pagamentos
    {"codigo": "pagamentos.read", "nome": "Visualizar Pagamentos", "recurso": "pagamentos", "acao": "read"},
    {"codigo": "pagamentos.create", "nome": "Criar Pagamentos", "recurso": "pagamentos", "acao": "create"},
    {"codigo": "pagamentos.update", "nome": "Atualizar Pagamentos", "recurso": "pagamentos", "acao": "update"},
    
    # Controle de Acesso
    {"codigo": "acesso.perfis", "nome": "Gerenciar Perfis", "recurso": "acesso", "acao": "perfis"},
    {"codigo": "acesso.permissoes", "nome": "Gerenciar Permissões", "recurso": "acesso", "acao": "permissoes"},
    {"codigo": "acesso.atribuir", "nome": "Atribuir Perfis", "recurso": "acesso", "acao": "atribuir"},
]


# ========== Definição de Perfis Padrão ==========

PERFIS = [
    {
        "nome": "Administrador",
        "codigo": "admin",
        "descricao": "Acesso completo ao sistema com todas as permissões",
        "sistema": True,
        "permissoes": [p["codigo"] for p in PERMISSOES],  # Todas as permissões
    },
    {
        "nome": "Gestor de Diárias",
        "codigo": "gestor_diarias",
        "descricao": "Gerencia diárias, empresas e inscrições de colaboradores",
        "sistema": True,
        "permissoes": [
            "diarias.read", "diarias.create", "diarias.update", "diarias.delete", "diarias.manage",
            "empresas.read", "empresas.create", "empresas.update",
            "usuarios.read",
            "presencas.read", "presencas.validar",
            "relatorios.read", "relatorios.export",
            "dashboard.read",
            "pagamentos.read", "pagamentos.create",
        ],
    },
    {
        "nome": "Gestor de Frota",
        "codigo": "gestor_frota",
        "descricao": "Gerencia veículos, rotas e alocações de transporte",
        "sistema": True,
        "permissoes": [
            "veiculos.read", "veiculos.create", "veiculos.update", "veiculos.delete",
            "rotas.read", "rotas.create", "rotas.update", "rotas.delete",
            "alocacoes.read", "alocacoes.create", "alocacoes.update", "alocacoes.delete",
            "usuarios.read",
            "diarias.read",
            "relatorios.read",
            "dashboard.read",
        ],
    },
    {
        "nome": "Supervisor",
        "codigo": "supervisor",
        "descricao": "Supervisiona operações e valida presenças",
        "sistema": True,
        "permissoes": [
            "diarias.read",
            "usuarios.read",
            "presencas.read", "presencas.marcar", "presencas.validar",
            "veiculos.read",
            "rotas.read",
            "alocacoes.read",
            "relatorios.read",
            "dashboard.read",
        ],
    },
    {
        "nome": "Colaborador",
        "codigo": "colaborador",
        "descricao": "Acesso básico para colaboradores",
        "sistema": True,
        "permissoes": [
            "diarias.read", "diarias.inscrever",
            "presencas.marcar",
            "dashboard.read",
        ],
    },
    {
        "nome": "Analista Financeiro",
        "codigo": "analista_financeiro",
        "descricao": "Gerencia pagamentos e visualiza relatórios financeiros",
        "sistema": True,
        "permissoes": [
            "pagamentos.read", "pagamentos.create", "pagamentos.update",
            "relatorios.read", "relatorios.export", "relatorios.gestao",
            "dashboard.read", "dashboard.executivo",
            "diarias.read",
            "usuarios.read",
        ],
    },
]


def criar_permissoes(db: Session, repo: PerfilRepository):
    """Cria todas as permissões do sistema."""
    print("📝 Criando permissões...")
    
    permissoes_criadas = 0
    permissoes_existentes = 0
    
    for perm_data in PERMISSOES:
        # Verifica se já existe
        existing = repo.get_permissao_by_codigo(perm_data["codigo"])
        if existing:
            permissoes_existentes += 1
            print(f"  ✓ Permissão '{perm_data['codigo']}' já existe")
            continue
        
        # Cria nova permissão
        repo.create_permissao(
            codigo=perm_data["codigo"],
            nome=perm_data["nome"],
            recurso=perm_data["recurso"],
            acao=perm_data["acao"],
            descricao=perm_data.get("descricao"),
        )
        permissoes_criadas += 1
        print(f"  ✓ Permissão '{perm_data['codigo']}' criada")
    
    print(f"\n✅ Permissões: {permissoes_criadas} criadas, {permissoes_existentes} já existiam")
    return permissoes_criadas > 0


def criar_perfis(db: Session, repo: PerfilRepository):
    """Cria todos os perfis padrão do sistema."""
    print("\n👥 Criando perfis...")
    
    perfis_criados = 0
    perfis_existentes = 0
    
    for perfil_data in PERFIS:
        # Verifica se já existe
        existing = repo.get_perfil_by_codigo(perfil_data["codigo"])
        if existing:
            perfis_existentes += 1
            print(f"  ✓ Perfil '{perfil_data['codigo']}' já existe")
            continue
        
        # Cria novo perfil
        perfil = repo.create_perfil(
            nome=perfil_data["nome"],
            codigo=perfil_data["codigo"],
            descricao=perfil_data.get("descricao"),
            sistema=perfil_data.get("sistema", False),
        )
        
        # Adiciona permissões ao perfil
        permissoes_ids = []
        for codigo_perm in perfil_data.get("permissoes", []):
            perm = repo.get_permissao_by_codigo(codigo_perm)
            if perm:
                permissoes_ids.append(perm.id)
        
        if permissoes_ids:
            repo.substituir_permissoes_do_perfil(perfil.id, permissoes_ids)
        
        perfis_criados += 1
        print(f"  ✓ Perfil '{perfil_data['codigo']}' criado com {len(permissoes_ids)} permissões")
    
    print(f"\n✅ Perfis: {perfis_criados} criados, {perfis_existentes} já existiam")


def main():
    """Função principal."""
    print("=" * 60)
    print("🚀 SEED DE PERFIS E PERMISSÕES")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        repo = PerfilRepository(db)
        
        # Cria permissões
        criar_permissoes(db, repo)
        
        # Cria perfis
        criar_perfis(db, repo)
        
        print("\n" + "=" * 60)
        print("✅ Seed de perfis e permissões concluído com sucesso!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erro ao executar seed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
