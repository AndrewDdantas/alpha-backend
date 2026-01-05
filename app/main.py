from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para Sistema de Gestão de Pessoas",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://localhost:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Inicializa serviços em background ao iniciar a aplicação."""
    from app.services.scheduler import iniciar_scheduler_em_background
    iniciar_scheduler_em_background()


@app.get("/", tags=["Health"])
async def root():
    """Endpoint de saúde da API."""
    return {"message": "Sistema de Gestão de Pessoas API", "status": "online"}


# Incluir rotas da API v1
app.include_router(api_router, prefix=settings.API_V1_STR)

