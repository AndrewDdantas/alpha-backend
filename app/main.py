from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import time
import logging

from app.api.v1.router import api_router
from app.core.config import settings
from app.services.metrics_service import metrics_service

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
        
        # Loga e registra métricas apenas para rotas da API
        path = request.url.path
        if path.startswith("/api/") and not path.startswith("/api/v1/metrics"):
            method = request.method
            perf_logger.info(f"{status} {method} {path}: {duration_ms:.2f}ms")
            
            # Registra no serviço de métricas
            metrics_service.record(
                path=path,
                method=method,
                duration_ms=duration_ms,
                status_code=response.status_code,
            )
        
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


from fastapi.responses import HTMLResponse

@app.get("/monitor", response_class=HTMLResponse, tags=["Monitoring"])
async def monitor_dashboard():
    """Dashboard visual de monitoramento da API."""
    overview = metrics_service.get_overview()
    endpoints = metrics_service.get_endpoint_stats()
    recent = metrics_service.get_recent_requests(limit=20)
    
    def get_color(ms):
        if ms < 100: return "#10b981"
        if ms < 500: return "#f59e0b"
        return "#ef4444"
    
    def get_method_color(method):
        colors = {"GET": "#61affe", "POST": "#49cc90", "PUT": "#fca130", "DELETE": "#f93e3e"}
        return colors.get(method, "#9b9b9b")
    
    endpoints_html = ""
    for ep in endpoints[:15]:
        method, path = ep["endpoint"].split(" ", 1)
        endpoints_html += f'''
        <div class="endpoint-row">
            <span class="method" style="background:{get_method_color(method)}">{method}</span>
            <span class="path">{path}</span>
            <span class="time" style="color:{get_color(ep['avg_ms'])}">{ep['avg_ms']}ms</span>
            <span class="count">({ep['count']}x)</span>
        </div>'''
    
    recent_html = ""
    for req in recent:
        status_class = "success" if 200 <= req["status_code"] < 400 else "error"
        recent_html += f'''
        <div class="recent-row">
            <span class="method" style="background:{get_method_color(req['method'])}">{req['method']}</span>
            <span class="path">{req['path']}</span>
            <span class="status {status_class}">{req['status_code']}</span>
            <span class="time" style="color:{get_color(req['duration_ms'])}">{req['duration_ms']}ms</span>
        </div>'''
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Monitor - SGP</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="refresh" content="10">
        <style>
            :root {{ --bg: #0f172a; --card: #1e293b; --border: #334155; --text: #f1f5f9; --muted: #94a3b8; }}
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); padding: 20px; }}
            h1 {{ font-size: 1.5rem; margin-bottom: 5px; }}
            .subtitle {{ color: var(--muted); font-size: 0.9rem; margin-bottom: 20px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 20px; }}
            .stat-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 15px; }}
            .stat-value {{ font-size: 1.8rem; font-weight: bold; }}
            .stat-label {{ color: var(--muted); font-size: 0.8rem; }}
            .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 15px; margin-bottom: 15px; }}
            .card-title {{ font-size: 1rem; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid var(--border); }}
            .endpoint-row, .recent-row {{ display: flex; align-items: center; gap: 10px; padding: 8px; border-radius: 5px; margin-bottom: 5px; background: rgba(255,255,255,0.03); }}
            .method {{ font-size: 0.65rem; padding: 3px 8px; border-radius: 4px; color: white; font-weight: 600; }}
            .path {{ flex: 1; font-family: monospace; font-size: 0.85rem; color: var(--muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
            .time {{ font-weight: 600; font-family: monospace; }}
            .count {{ font-size: 0.75rem; color: var(--muted); }}
            .status {{ font-size: 0.75rem; padding: 2px 6px; border-radius: 4px; }}
            .status.success {{ background: #10b98133; color: #10b981; }}
            .status.error {{ background: #ef444433; color: #ef4444; }}
            .refresh-note {{ text-align: center; color: var(--muted); font-size: 0.8rem; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <h1>⚡ API Performance Monitor</h1>
        <p class="subtitle">Sistema de Gestão de Pessoas - Atualiza a cada 10s</p>
        
        <div class="grid">
            <div class="stat-card">
                <div class="stat-value">{overview['total_requests']}</div>
                <div class="stat-label">📈 Total Requests</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color:{get_color(overview['avg_duration_ms'])}">{overview['avg_duration_ms']}ms</div>
                <div class="stat-label">⚡ Tempo Médio</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color:#10b981">{overview['success_rate']}%</div>
                <div class="stat-label">✅ Taxa Sucesso</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color:{'#ef4444' if overview['slow_requests'] > 0 else '#10b981'}">{overview['slow_requests']}</div>
                <div class="stat-label">🐌 Requests Lentos</div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title">🔥 Endpoints por Tempo (mais lentos primeiro)</div>
            {endpoints_html if endpoints_html else '<p style="color:var(--muted)">Nenhum endpoint registrado ainda</p>'}
        </div>
        
        <div class="card">
            <div class="card-title">📝 Requisições Recentes</div>
            {recent_html if recent_html else '<p style="color:var(--muted)">Nenhuma requisição registrada ainda</p>'}
        </div>
        
        <p class="refresh-note">🔄 Esta página atualiza automaticamente a cada 10 segundos</p>
    </body>
    </html>
    '''
    return html


@app.get("/api/v1/metrics", tags=["Monitoring"])
async def get_metrics():
    """Retorna métricas de performance da API."""
    return {
        "overview": metrics_service.get_overview(),
        "endpoints": metrics_service.get_endpoint_stats(),
        "recent": metrics_service.get_recent_requests(limit=30),
        "timeline": metrics_service.get_timeline(minutes=10),
    }


@app.get("/api/v1/metrics/overview", tags=["Monitoring"])
async def get_metrics_overview():
    """Retorna visão geral das métricas."""
    return metrics_service.get_overview()


@app.get("/api/v1/metrics/endpoints", tags=["Monitoring"])
async def get_metrics_endpoints():
    """Retorna estatísticas por endpoint."""
    return metrics_service.get_endpoint_stats()


# Incluir rotas da API v1
app.include_router(api_router, prefix=settings.API_V1_STR)
