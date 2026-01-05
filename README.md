# Alpha Backend - API FastAPI

Sistema de gestão de diárias, colaboradores e transporte.

## Requisitos

- Python 3.9+
- PostgreSQL (Supabase)

## Setup

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

## Configuração

Copie `.env.example` para `.env` e configure as variáveis:

```bash
cp .env.example .env
```

## Executar

```bash
uvicorn app.main:app --host=0.0.0.0 --reload
```

API disponível em: http://localhost:8000

Documentação: http://localhost:8000/docs

## Estrutura

```
backend/
├── app/
│   ├── api/v1/endpoints/   # Endpoints da API
│   ├── core/               # Configurações, autenticação
│   ├── models/             # Modelos SQLAlchemy
│   ├── schemas/            # Schemas Pydantic
│   ├── services/           # Lógica de negócio
│   └── main.py             # Ponto de entrada
├── scripts/                # Scripts utilitários
├── requirements.txt
└── .env
```
