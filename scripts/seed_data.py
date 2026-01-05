"""
Seed script para criar dados de teste.
LIMPA DADOS EXISTENTES antes de criar novos.
Execute com: python scripts/seed_data.py
"""
import sys
sys.path.insert(0, ".")

from datetime import time
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models.empresa import Empresa
from app.models.turno import Turno
from app.models.pessoa import Pessoa
from app.models.veiculo import Veiculo
from app.models.rota import Rota, PontoParada
from app.models.enums import TipoPessoa
from app.core.security import get_password_hash


def clear_data():
    """Limpa dados existentes."""
    print("Limpando dados existentes...")
    
    tabelas = [
        "alocacoes_colaboradores",
        "alocacoes_diarias", 
        "inscricoes",
        "diarias",
        # "pontos_onibus" - NÃO limpar! Cache do OSM deve ser preservado
        "pessoas",
        "pontos_parada",
        "rotas",
        "veiculos",
        "turnos",
        "empresas",
    ]
    
    for tabela in tabelas:
        try:
            with engine.connect() as conn:
                conn.execute(text(f"TRUNCATE TABLE {tabela} CASCADE"))
                conn.commit()
        except:
            pass


def seed_data():
    """Popula banco com dados de teste."""
    
    clear_data()
    
    db = SessionLocal()
    
    try:
        # ========== EMPRESA ==========
        print("Criando empresa...")
        empresa = Empresa(
            nome="Alpha Transportes",
            cnpj="12345678000199",
            razao_social="Alpha Transportes LTDA",
            email="contato@alpha.com.br",
            telefone="(11) 99999-9999",
            cidade="São Paulo",
            estado="SP",
            contato_nome="Carlos Silva",
        )
        db.add(empresa)
        db.flush()
        
        # ========== TURNOS ==========
        print("Criando turnos...")
        turnos_data = [
            ("Manhã", "06:00", "14:00"),
            ("Tarde", "14:00", "22:00"),
            ("Noite", "22:00", "06:00"),
            ("Comercial", "08:00", "18:00"),
            ("Administrativo", "09:00", "17:00"),
        ]
        
        for nome, inicio, fim in turnos_data:
            h1, m1 = map(int, inicio.split(":"))
            h2, m2 = map(int, fim.split(":"))
            turno = Turno(
                empresa_id=empresa.id,
                nome=nome,
                hora_inicio=time(h1, m1),
                hora_fim=time(h2, m2),
            )
            db.add(turno)
        
        # ========== VEÍCULOS ==========
        print("Criando veículos...")
        veiculos_data = [
            ("ABC-1234", "Mercedes Sprinter", "Branca", 20, "José Motorista", "(11) 98888-1111"),
            ("DEF-5678", "Volkswagen Volksbus", "Prata", 30, "Maria Motorista", "(11) 98888-2222"),
            ("GHI-9012", "Ford Transit", "Cinza", 15, "Pedro Motorista", "(11) 98888-3333"),
        ]
        
        for placa, modelo, cor, capacidade, motorista, tel in veiculos_data:
            veiculo = Veiculo(
                placa=placa,
                modelo=modelo,
                cor=cor,
                capacidade=capacidade,
                motorista=motorista,
                telefone_motorista=tel,
            )
            db.add(veiculo)
        
        # ========== ROTAS ==========
        print("Criando rotas...")
        rotas_data = [
            ("Rota Centro", "Saindo do centro", [
                ("Terminal Central", -23.5505, -46.6334, "06:30"),
                ("Shopping Centro", -23.5515, -46.6344, "06:45"),
                ("Praça da Sé", -23.5504, -46.6336, "07:00"),
            ]),
            ("Rota Zona Norte", "Região norte", [
                ("Shopping Norte", -23.4905, -46.6234, "06:00"),
                ("Metrô Santana", -23.5005, -46.6134, "06:20"),
                ("Parque Norte", -23.5105, -46.6034, "06:40"),
            ]),
            ("Rota Zona Sul", "Região sul", [
                ("Terminal Sul", -23.6505, -46.6534, "06:15"),
                ("Shopping Sul", -23.6305, -46.6434, "06:35"),
                ("Parque Ibirapuera", -23.5877, -46.6576, "06:55"),
            ]),
            ("Rota Zona Leste", "Região leste", [
                ("Terminal Leste", -23.5405, -46.4734, "05:45"),
                ("Metrô Itaquera", -23.5405, -46.4534, "06:10"),
                ("Shopping Leste", -23.5405, -46.4334, "06:30"),
            ]),
        ]
        
        pontos_criados = []
        for rota_nome, descricao, pontos in rotas_data:
            rota = Rota(nome=rota_nome, descricao=descricao)
            db.add(rota)
            db.flush()
            
            for ordem, (ponto_nome, lat, lng, horario) in enumerate(pontos, 1):
                ponto = PontoParada(
                    rota_id=rota.id,
                    nome=ponto_nome,
                    latitude=lat,
                    longitude=lng,
                    horario=horario,
                    ordem=ordem,
                )
                db.add(ponto)
                db.flush()
                pontos_criados.append(ponto)
        
        # ========== ADMIN ==========
        print("Criando admin...")
        admin = Pessoa(
            nome="Administrador",
            email="admin@alpha.com.br",
            cpf="00000000000",
            telefone="(11) 99999-0000",
            senha_hash=get_password_hash("admin123"),
            tipo_pessoa=TipoPessoa.ADMIN,
            ativo=True,
        )
        db.add(admin)
        db.flush()
        
        # ========== FUNCIONÁRIOS ==========
        print("Criando 30 funcionários...")
        pessoas_criadas = []
        nomes = [
            "Ana Silva", "Bruno Santos", "Carla Oliveira", "Daniel Costa", "Elena Ferreira",
            "Fernando Lima", "Gabriela Souza", "Hugo Almeida", "Isabela Martins", "João Pereira",
            "Karen Ribeiro", "Lucas Gomes", "Marina Rocha", "Nelson Dias", "Olívia Fernandes",
            "Paulo Cardoso", "Queila Barbosa", "Ricardo Moreira", "Sandra Nascimento", "Thiago Araújo",
            "Úrsula Melo", "Victor Teixeira", "Wanda Correia", "Xavier Monteiro", "Yara Freitas",
            "Zeca Cavalcanti", "Amanda Lopes", "Breno Azevedo", "Camila Duarte", "Diego Mendes",
        ]
        
        for i, nome in enumerate(nomes):
            email = nome.lower().replace(" ", ".").replace("ú", "u").replace("é", "e") + "@alpha.com.br"
            cpf = f"{10000000000 + i}"
            ponto_parada = pontos_criados[i % len(pontos_criados)] if pontos_criados else None
            
            pessoa = Pessoa(
                nome=nome,
                email=email,
                cpf=cpf,
                telefone=f"(11) 9{7000 + i:04d}-{1000 + i:04d}",
                senha_hash=get_password_hash("123456"),
                tipo_pessoa=TipoPessoa.COLABORADOR,
                ativo=True,
                ponto_parada_id=ponto_parada.id if ponto_parada else None,
            )
            db.add(pessoa)
            db.flush()
            pessoas_criadas.append(pessoa)
        
        # ========== DIÁRIAS ==========
        print("Criando diárias...")
        from datetime import date as date_type, timedelta
        from app.models.diaria import Diaria, Inscricao
        from app.models.enums import StatusDiaria, StatusInscricao
        
        # Diária para hoje
        diaria_hoje = Diaria(
            titulo="Manutenção Industrial - Turno Manhã",
            descricao="Serviço de manutenção preventiva",
            data=date_type.today(),
            horario_inicio=time(6, 0),
            horario_fim=time(14, 0),
            vagas=20,
            valor=150.00,
            local="Fábrica São Paulo - Zona Leste",
            empresa_id=empresa.id,
            status=StatusDiaria.FECHADA,  # Fechada para permitir registro de presença
        )
        db.add(diaria_hoje)
        db.flush()
        
        # Inscreve 10 funcionários na diária de hoje
        for i, pessoa in enumerate(pessoas_criadas[:10]):
            inscricao = Inscricao(
                diaria_id=diaria_hoje.id,
                pessoa_id=pessoa.id,
                status=StatusInscricao.CONFIRMADA,
            )
            db.add(inscricao)
        
        # Define o primeiro inscrito como supervisor da diária E muda o tipo_pessoa
        pessoas_criadas[0].tipo_pessoa = TipoPessoa.SUPERVISOR
        diaria_hoje.supervisor_id = pessoas_criadas[0].id
        
        # Diária para amanhã
        diaria_amanha = Diaria(
            titulo="Montagem de Equipamentos - Turno Tarde",
            descricao="Montagem de linha de produção",
            data=date_type.today() + timedelta(days=1),
            horario_inicio=time(14, 0),
            horario_fim=time(22, 0),
            vagas=15,
            valor=180.00,
            local="Centro de Distribuição - Guarulhos",
            empresa_id=empresa.id,
            status=StatusDiaria.ABERTA,
        )
        db.add(diaria_amanha)
        
        db.commit()
        
        print()
        print("=" * 50)
        print("✅ Seed executado com sucesso!")
        print("=" * 50)
        print()
        print("Dados criados:")
        print(f"  • 1 Empresa: Alpha Transportes")
        print(f"  • 5 Turnos")
        print(f"  • 3 Veículos")
        print(f"  • 4 Rotas com pontos de parada")
        print(f"  • 1 Admin: admin@alpha.com.br / admin123")
        print(f"  • 30 Funcionários (senha: 123456)")
        print(f"  • 2 Diárias (hoje e amanhã)")
        print(f"  • 10 Inscrições na diária de hoje (FECHADA)")
        print()
        print("Para testar presença:")
        print(f"  • Login: ana.silva@alpha.com.br / 123456")
        print(f"  • Ela é supervisora da diária de hoje")
        print()
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
