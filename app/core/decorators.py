"""
Decoradores de performance e logging para a API.
"""
import time
import functools
import logging
from typing import Callable, Any

# Configura logger
logger = logging.getLogger("performance")
logger.setLevel(logging.INFO)

# Handler para console com formatação
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '⏱️  %(message)s'
    ))
    logger.addHandler(handler)


def timing(func: Callable) -> Callable:
    """
    Decorador que mede e loga o tempo de execução de uma função.
    Funciona tanto com funções síncronas quanto assíncronas.
    
    Uso:
        @timing
        async def meu_endpoint():
            ...
    """
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs) -> Any:
        start_time = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            # Indica performance com cores
            if duration_ms < 100:
                status = "🟢"  # Rápido
            elif duration_ms < 500:
                status = "🟡"  # Médio
            else:
                status = "🔴"  # Lento
            
            logger.info(f"{status} {func.__name__}: {duration_ms:.2f}ms")
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs) -> Any:
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            if duration_ms < 100:
                status = "🟢"
            elif duration_ms < 500:
                status = "🟡"
            else:
                status = "🔴"
            
            logger.info(f"{status} {func.__name__}: {duration_ms:.2f}ms")
    
    # Retorna wrapper adequado baseado no tipo da função
    if asyncio_iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


def asyncio_iscoroutinefunction(func: Callable) -> bool:
    """Verifica se a função é assíncrona."""
    import asyncio
    return asyncio.iscoroutinefunction(func)


def timing_with_threshold(threshold_ms: float = 200):
    """
    Decorador que só loga quando a execução ultrapassa um threshold.
    
    Uso:
        @timing_with_threshold(threshold_ms=100)
        async def meu_endpoint():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000
                
                if duration_ms >= threshold_ms:
                    logger.warning(f"⚠️  SLOW: {func.__name__}: {duration_ms:.2f}ms (threshold: {threshold_ms}ms)")
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000
                
                if duration_ms >= threshold_ms:
                    logger.warning(f"⚠️  SLOW: {func.__name__}: {duration_ms:.2f}ms (threshold: {threshold_ms}ms)")
        
        if asyncio_iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator
