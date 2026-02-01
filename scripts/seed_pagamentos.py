
import sys
sys.path.insert(0, ".")

from datetime import date, timedelta, time
import random
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models.empresa import Empresa
from app.models.pessoa import Pessoa
from app.models.diaria import Diaria, Inscricao
from app.models.enums import TipoPessoa, StatusDiaria, StatusInscricao
from app.core.security import get_password_hash

def seed_pagamentos():
    print("🌱 Iniciando seed de pagamentos...")
    db = SessionLocal()
    
    try:
        # 1. Garante que existe uma empresa
        empresa = db.query(Empresa).first()
        if not empresa:
            empresa = Empresa(
                nome="Alpha Transportes",
                cnpj="12345678000199",
                razao_social="Alpha Transportes LTDA",
                email="contato@alpha.com.br",
                cidade="São Paulo",
                estado="SP"
            )
            db.add(empresa)
            db.flush()

        # 2. Cria o usuário de teste
        email_teste = "colab.pagto@alpha.com.br"
        colaborador = db.query(Pessoa).filter(Pessoa.email == email_teste).first()
        
        if not colaborador:
            print(f"Criando usuário de teste: {email_teste}")
            colaborador = Pessoa(
                nome="Colaborador Teste Pagamento",
                email=email_teste,
                cpf="99988877700",
                telefone="(11) 99999-9999",
                senha_hash=get_password_hash("123456"),
                tipo_pessoa=TipoPessoa.COLABORADOR,
                ativo=True
            )
            db.add(colaborador)
            db.flush()
        else:
            print(f"Usuário encontrado: {colaborador.nome}")

        # 3. Gerar diárias passadas para simular pagamentos
        # Vamos criar dados para o mês atual e anterior
        hoje = date.today()
        meses = [hoje, (hoje.replace(day=1) - timedelta(days=1))]
        
        diarias_criadas = 0
        
        for base_date in meses:
            # 1ª Quinzena (Dia 5 e 10)
            datas_1q = [
                base_date.replace(day=5),
                base_date.replace(day=10)
            ]
            
            # 2ª Quinzena (Dia 20 e 25)
            # Cuidado com fevereiro/meses com menos dias, simplificando para dia 20 e 25 que todo mês tem
            datas_2q = [
                base_date.replace(day=20),
                base_date.replace(day=25)
            ]
            
            # Junta todas
            datas_para_criar = datas_1q + datas_2q
            
            for data_diaria in datas_para_criar:
                # Pula datas futuras se houver
                if data_diaria > hoje:
                    continue
                    
                # Cria Diária Concluída
                diaria = Diaria(
                    titulo=f"Diária {data_diaria.strftime('%d/%m')} - Tarde",
                    descricao="Serviço executado",
                    data=data_diaria,
                    horario_inicio=time(14, 0),
                    horario_fim=time(22, 0),
                    vagas=5,
                    valor=200.00, # Valor fixo para facilitar conta
                    local="CD Teste",
                    empresa_id=empresa.id,
                    status=StatusDiaria.CONCLUIDA
                )
                db.add(diaria)
                db.flush()
                
                # Inscreve o colaborador e conclui
                inscricao = Inscricao(
                    diaria_id=diaria.id,
                    pessoa_id=colaborador.id,
                    status=StatusInscricao.CONCLUIDA,
                    observacao="Presença confirmada"
                )
                db.add(inscricao)
                diarias_criadas += 1

        db.commit()
        print(f"✅ Sucesso! {diarias_criadas} diárias criadas/simuladas.")
        print("-" * 30)
        print("Login para teste:")
        print(f"Email: {email_teste}")
        print("Senha: 123456")
        print("-" * 30)

    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao rodar seed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_pagamentos()
