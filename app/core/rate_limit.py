"""Rate limiting simples em memória para rotas sensíveis."""

from collections import defaultdict
from time import time

from fastapi import HTTPException, Request, status


class RateLimiter:
  def __init__(self, max_requests: int, window_seconds: int):
    self.max_requests = max_requests
    self.window_seconds = window_seconds
    self._requests: dict[str, list[float]] = defaultdict(list)

  def check(self, key: str) -> None:
    now = time()
    window_start = now - self.window_seconds
    self._requests[key] = [t for t in self._requests[key] if t > window_start]

    if len(self._requests[key]) >= self.max_requests:
      raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Muitas tentativas. Aguarde alguns minutos e tente novamente.",
      )

    self._requests[key].append(now)


def client_ip(request: Request) -> str:
  forwarded = request.headers.get("X-Forwarded-For")
  if forwarded:
    return forwarded.split(",")[0].strip()
  if request.client:
    return request.client.host
  return "unknown"


auth_rate_limiter = RateLimiter(max_requests=10, window_seconds=60)


async def rate_limit_auth(request: Request) -> None:
  auth_rate_limiter.check(client_ip(request))
