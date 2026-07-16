"""Cliente HTTP para o serviço WhatsApp (Baileys)."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


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
        self.base_url = (base_url or settings.WHATSAPP_SERVICE_URL).rstrip("/")
        self.token = token or settings.WHATSAPP_SERVICE_TOKEN
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _request(self, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(
                    method,
                    url,
                    headers=self._headers(),
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
        return self._request("GET", "/status")

    def get_qr(self) -> Dict[str, Any]:
        return self._request("GET", "/qr")

    def logout(self) -> Dict[str, Any]:
        return self._request("POST", "/logout")

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
