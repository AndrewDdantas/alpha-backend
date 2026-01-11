"""
Serviço de métricas de performance da API.
Armazena métricas em memória para monitoramento em tempo real.
"""
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from threading import Lock
import statistics


@dataclass
class RequestMetric:
    """Representa uma métrica de requisição."""
    path: str
    method: str
    duration_ms: float
    status_code: int
    timestamp: datetime = field(default_factory=datetime.utcnow)


class MetricsService:
    """Serviço para coleta e análise de métricas de performance."""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializa o serviço."""
        # Armazena últimas 1000 requisições
        self.requests: deque[RequestMetric] = deque(maxlen=1000)
        # Métricas por endpoint
        self.endpoint_stats: Dict[str, List[float]] = {}
        # Lock para thread-safety
        self.lock = Lock()
    
    def record(self, path: str, method: str, duration_ms: float, status_code: int):
        """Registra uma nova métrica de requisição."""
        metric = RequestMetric(
            path=path,
            method=method,
            duration_ms=duration_ms,
            status_code=status_code,
        )
        
        with self.lock:
            self.requests.append(metric)
            
            # Atualiza estatísticas por endpoint
            key = f"{method} {path}"
            if key not in self.endpoint_stats:
                self.endpoint_stats[key] = []
            
            # Mantém últimas 100 medições por endpoint
            if len(self.endpoint_stats[key]) >= 100:
                self.endpoint_stats[key].pop(0)
            self.endpoint_stats[key].append(duration_ms)
    
    def get_overview(self) -> dict:
        """Retorna visão geral das métricas."""
        with self.lock:
            if not self.requests:
                return {
                    "total_requests": 0,
                    "avg_duration_ms": 0,
                    "min_duration_ms": 0,
                    "max_duration_ms": 0,
                    "success_rate": 100,
                    "slow_requests": 0,
                }
            
            durations = [r.duration_ms for r in self.requests]
            success_count = sum(1 for r in self.requests if 200 <= r.status_code < 400)
            slow_count = sum(1 for r in self.requests if r.duration_ms > 500)
            
            return {
                "total_requests": len(self.requests),
                "avg_duration_ms": round(statistics.mean(durations), 2),
                "min_duration_ms": round(min(durations), 2),
                "max_duration_ms": round(max(durations), 2),
                "success_rate": round((success_count / len(self.requests)) * 100, 1),
                "slow_requests": slow_count,
            }
    
    def get_endpoint_stats(self) -> List[dict]:
        """Retorna estatísticas por endpoint."""
        with self.lock:
            result = []
            for endpoint, durations in self.endpoint_stats.items():
                if not durations:
                    continue
                    
                result.append({
                    "endpoint": endpoint,
                    "count": len(durations),
                    "avg_ms": round(statistics.mean(durations), 2),
                    "min_ms": round(min(durations), 2),
                    "max_ms": round(max(durations), 2),
                    "p95_ms": round(sorted(durations)[int(len(durations) * 0.95)] if len(durations) >= 2 else durations[0], 2),
                })
            
            # Ordena por média de tempo (mais lentos primeiro)
            result.sort(key=lambda x: x["avg_ms"], reverse=True)
            return result
    
    def get_recent_requests(self, limit: int = 50) -> List[dict]:
        """Retorna requisições recentes."""
        with self.lock:
            requests = list(self.requests)[-limit:]
            return [
                {
                    "path": r.path,
                    "method": r.method,
                    "duration_ms": round(r.duration_ms, 2),
                    "status_code": r.status_code,
                    "timestamp": r.timestamp.isoformat(),
                }
                for r in reversed(requests)
            ]
    
    def get_timeline(self, minutes: int = 5) -> List[dict]:
        """Retorna timeline de requisições agrupadas por minuto."""
        from datetime import timedelta
        
        with self.lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(minutes=minutes)
            
            # Agrupa por minuto
            by_minute: Dict[str, List[float]] = {}
            for r in self.requests:
                if r.timestamp >= cutoff:
                    minute_key = r.timestamp.strftime("%H:%M")
                    if minute_key not in by_minute:
                        by_minute[minute_key] = []
                    by_minute[minute_key].append(r.duration_ms)
            
            return [
                {
                    "time": minute,
                    "count": len(durations),
                    "avg_ms": round(statistics.mean(durations), 2) if durations else 0,
                }
                for minute, durations in sorted(by_minute.items())
            ]


# Singleton instance
metrics_service = MetricsService()
