"""Proteção de endpoints de monitoramento e métricas."""

from fastapi import HTTPException, Request, status

from app.core.config import settings


async def require_metrics_access(request: Request) -> None:
  """Exige chave de API em produção; em dev permite acesso sem chave."""
  if not settings.is_production and not settings.METRICS_API_KEY:
    return

  if not settings.METRICS_API_KEY:
    raise HTTPException(
      status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
      detail="Monitoramento desabilitado: configure METRICS_API_KEY",
    )

  provided = request.headers.get("X-Metrics-Key")
  if provided != settings.METRICS_API_KEY:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Chave de monitoramento inválida",
    )
