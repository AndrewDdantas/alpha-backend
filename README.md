# Alpha Backend - API FastAPI

Sistema de gestao de diarias, colaboradores, presencas e transporte fretado.

## Requisitos

- Python 3.9+
- PostgreSQL, local ou Supabase
- MinIO/S3 compativel para upload de fotos, caso use presencas/fotos

## Setup

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## Configuracao

Copie `.env.example` para `.env` e configure as variaveis do seu ambiente:

```bash
cp .env.example .env
```

Variaveis importantes:

- `DATABASE_URL`: connection string do PostgreSQL. Para Supabase, prefira o Session Pooler.
- `SECRET_KEY`: chave forte para assinar tokens JWT.
- `BACKEND_CORS_ORIGINS`: origens permitidas para o frontend.
- `MINIO_*`: configuracao do storage S3 compativel.
- `GOOGLE_MAPS_API_KEY`: usada no calculo de rotas, quando disponivel.
- `EMAIL_*` e `RESEND_API_KEY`: usadas no fluxo de recuperacao de senha.

## Executar

```bash
uvicorn app.main:app --host=0.0.0.0 --reload
```

API disponivel em: http://localhost:8000

Documentacao: http://localhost:8000/docs

Monitor de performance: http://localhost:8000/monitor

## Migrations

O projeto usa Alembic para versionar o schema do banco.

```bash
# Aplicar migrations pendentes
alembic upgrade head

# Criar uma nova migration a partir dos models
alembic revision --autogenerate -m "descricao da alteracao"
```

Se o banco ja existir com esse schema, valide a compatibilidade antes e marque a
baseline sem recriar tabelas:

```bash
alembic stamp head
```

## Testes

```bash
pytest
```

## Estrutura

```text
alpha-backend/
|-- app/
|   |-- api/v1/endpoints/  # Endpoints da API
|   |-- core/              # Configuracao, autenticacao e permissoes
|   |-- db/                # Sessao e base SQLAlchemy
|   |-- models/            # Modelos SQLAlchemy
|   |-- repositories/      # Acesso ao banco de dados
|   |-- schemas/           # Schemas Pydantic
|   |-- services/          # Regras de negocio e integracoes
|   `-- main.py            # Ponto de entrada
|-- deploy/                # Nginx, systemd e setup Ubuntu
|-- requirements.txt
|-- .env.example
`-- README.md
```

## Deploy

A pasta `deploy/` contem um script de setup para Ubuntu/Lightsail, alem de arquivos de Nginx e systemd. Revise o `.env` no servidor antes de iniciar o servico.
