"""Cliente HTTP para o serviço WhatsApp (Baileys)."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, urlunparse

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# Cliente compartilhado — evita TCP/handshake a cada request (ganho grande no Windows).
_shared_client: Optional[httpx.Client] = None


def _normalize_service_url(url: str) -> str:
    """Evita latência de localhost→IPv6 no Windows usando 127.0.0.1."""
    parsed = urlparse(url.rstrip("/"))
    host = parsed.hostname or ""
    if host.lower() == "localhost":
        netloc = parsed.netloc.replace("localhost", "127.0.0.1", 1)
        netloc = netloc.replace("Localhost", "127.0.0.1", 1)
        return urlunparse(parsed._replace(netloc=netloc)).rstrip("/")
    return url.rstrip("/")


def _get_shared_client(timeout: float) -> httpx.Client:
    global _shared_client
    if _shared_client is None or _shared_client.is_closed:
        _shared_client = httpx.Client(
            timeout=httpx.Timeout(timeout, connect=5.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )
    return _shared_client


class WhatsAppClientError(Exception):
    """Erro ao comunicar com o serviço WhatsApp."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class WhatsAppClient:
    """Wrappers para status, QR, logout e envio de mensagens."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        timeout: float = 60.0,
    ):
        self.base_url = _normalize_service_url(
            base_url or settings.WHATSAPP_SERVICE_URL
        )
        self.token = token or settings.WHATSAPP_SERVICE_TOKEN
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _request(
        self,
        method: str,
        path: str,
        *,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        req_timeout = timeout if timeout is not None else self.timeout
        try:
            client = _get_shared_client(self.timeout)
            response = client.request(
                method,
                url,
                headers=self._headers(),
                timeout=req_timeout,
                **kwargs,
            )
        except httpx.RequestError as exc:
            logger.error("WhatsApp service unreachable: %s", exc)
            raise WhatsAppClientError(
                "Serviço WhatsApp indisponível. Verifique se está em execução."
            ) from exc

        if response.status_code >= 400:
            detail = "Erro no serviço WhatsApp"
            try:
                payload = response.json()
                detail = payload.get("detail") or payload.get("message") or detail
            except Exception:
                detail = response.text or detail
            raise WhatsAppClientError(detail, status_code=response.status_code)

        if not response.content:
            return {}
        return response.json()

    def get_status(self) -> Dict[str, Any]:
        return self._request("GET", "/status", timeout=5.0)

    def get_qr(self) -> Dict[str, Any]:
        return self._request("GET", "/qr", timeout=5.0)

    def logout(self) -> Dict[str, Any]:
        return self._request("POST", "/logout", timeout=15.0)

    def send_messages(self, numbers: List[str], message: str) -> Dict[str, Any]:
        return self._request(
            "POST",
            "/send",
            json={"numbers": numbers, "message": message},
        )

    def send_to_jids(self, jids: List[str], message: str) -> Dict[str, Any]:
        return self._request(
            "POST",
            "/send",
            json={"jids": jids, "message": message},
        )

    def resolve_numbers(self, numbers: List[str]) -> Dict[str, Any]:
        return self._request(
            "POST",
            "/resolve",
            json={"numbers": numbers},
        )
