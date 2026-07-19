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

- `POSTGRES_*`: dados usados para montar a connection string local do PostgreSQL.
- `DATABASE_URL`: override opcional da connection string. Para Supabase, prefira o Session Pooler.
- `SECRET_KEY`: chave forte para assinar tokens JWT.
- `MASTER_ADMIN_*`: dados usados pelo bootstrap da conta master/admin inicial.
- `BACKEND_CORS_ORIGINS`: origens permitidas para o frontend.
- `MINIO_*`: configuracao do storage S3 compativel.
- `GOOGLE_MAPS_API_KEY`: usada no calculo de rotas, quando disponivel.
- `EMAIL_*` e `RESEND_API_KEY`: usadas no fluxo de recuperacao de senha.
- `WHATSAPP_ENABLED`, `WHATSAPP_SERVICE_URL`, `WHATSAPP_SERVICE_TOKEN`: notificacoes via Baileys (servico em `../whatsapp-service`).

## WhatsApp (Baileys)

O envio de mensagens roda em um servico Node separado (`Alpha/whatsapp-service`).

```bash
# Em outro terminal
cd ../whatsapp-service
cp .env.example .env
npm install
npm run dev
```

No `.env` do backend:

```env
WHATSAPP_ENABLED=true
WHATSAPP_SERVICE_URL=http://localhost:3100
WHATSAPP_SERVICE_TOKEN=change-me-whatsapp-token
```

No admin do frontend: **Cadastro → WhatsApp** para escanear o QR.
Ao criar uma diaria, colaboradores ativos com telefone sao notificados em background.
Tambem ha botao de reenvio manual em **Cadastro → Diarias**.

Opcionalmente, o servico sobe com `docker compose` (service `whatsapp`, porta 3100, volume `whatsapp_auth`).

## Infra local com Docker

O `docker-compose.yml` usa o mesmo `.env` do projeto para subir Postgres, MinIO,
WhatsApp e a API.

```bash
# Se ainda nao existir .env
cp .env.example .env

# Build e sobe tudo (incluindo a API)
docker compose up -d --build

# Ver status dos servicos
docker compose ps

# Criar ou atualizar a conta master/admin inicial
docker compose exec api python -m app.scripts.create_admin
```

A API aplica as migrations automaticamente no startup do container.

### Traefik

O service `api` entra na rede externa do Traefik (`TRAEFIK_NETWORK`, padrao `web`)
e expoe `TRAEFIK_HOST` em `websecure` com `letsencrypt`.

O redirect HTTP→HTTPS ja vem no entrypoint do Traefik, entao nao precisa de
middleware extra na API.

Se a rede do Traefik nao tiver `name: web` fixo, confira o nome real:

```bash
docker network ls | findstr web
```

E ajuste `TRAEFIK_NETWORK` no `.env` se necessario.

Se preferir rodar a API no host (uvicorn local), suba so a infra:

```bash
docker compose up -d postgres minio minio-init whatsapp
alembic upgrade head
python -m app.scripts.create_admin
```

Servicos locais:

- API: http://localhost:${API_PORT:-8000}
- Postgres: `localhost:${POSTGRES_PORT}`
- MinIO API: http://localhost:9000
- MinIO Console: http://localhost:9001
- WhatsApp: http://localhost:${WHATSAPP_PORT:-3100}

Para parar os servicos:

```bash
docker compose down
```

Para remover tambem os dados persistidos em volumes:

```bash
docker compose down -v
```

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
