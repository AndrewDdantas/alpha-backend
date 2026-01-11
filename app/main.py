from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import time
import logging

from app.api.v1.router import api_router
from app.core.config import settings

# Logger para performance
perf_logger = logging.getLogger("performance")
perf_logger.setLevel(logging.INFO)
if not perf_logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('⏱️  %(message)s'))
    perf_logger.addHandler(handler)


class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware que mede o tempo de execução de cada request."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        response = await call_next(request)
        
        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        
        # Indica performance com cores
        if duration_ms < 100:
            status = "🟢"  # Rápido
        elif duration_ms < 500:
            status = "🟡"  # Médio
        else:
            status = "🔴"  # Lento
        
        # Loga apenas rotas da API (não arquivos estáticos, health checks)
        path = request.url.path
        if path.startswith("/api/"):
            method = request.method
            perf_logger.info(f"{status} {method} {path}: {duration_ms:.2f}ms")
        
        return response


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
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de timing para medir performance de todas as rotas
app.add_middleware(TimingMiddleware)


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

