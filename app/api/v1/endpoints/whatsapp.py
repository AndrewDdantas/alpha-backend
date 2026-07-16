"""Endpoints admin para gestão/proxy do WhatsApp e notificações de diária."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_db
from app.core.permissions import require_admin
from app.models.pessoa import Pessoa
from app.services.whatsapp_client import WhatsAppClient, WhatsAppClientError
from app.services.whatsapp_notification_service import WhatsAppNotificationService

router = APIRouter()


def _client() -> WhatsAppClient:
    return WhatsAppClient()


@router.get("/whatsapp/status")
def whatsapp_status(
    current_user: Pessoa = Depends(require_admin()),
):
    """Status da sessão WhatsApp (proxy)."""
    try:
        data = _client().get_status()
        data["enabled"] = settings.WHATSAPP_ENABLED
        return data
    except WhatsAppClientError as exc:
        raise HTTPException(
            status_code=exc.status_code or status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.get("/whatsapp/qr")
def whatsapp_qr(
    current_user: Pessoa = Depends(require_admin()),
):
    """QR Code atual para pareamento (proxy)."""
    try:
        data = _client().get_qr()
        data["enabled"] = settings.WHATSAPP_ENABLED
        return data
    except WhatsAppClientError as exc:
        raise HTTPException(
            status_code=exc.status_code or status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.post("/whatsapp/logout")
def whatsapp_logout(
    current_user: Pessoa = Depends(require_admin()),
):
    """Encerra sessão WhatsApp e solicita novo QR."""
    try:
        return _client().logout()
    except WhatsAppClientError as exc:
        raise HTTPException(
            status_code=exc.status_code or status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.post("/whatsapp/sync-jids")
def sync_whatsapp_jids(
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """
    Resolve e grava whatsapp_jid para todas as pessoas com telefone
    (via Baileys onWhatsApp). Útil para base já existente.
    """
    if not settings.WHATSAPP_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="WhatsApp está desabilitado (WHATSAPP_ENABLED=false)",
        )

    from app.services.whatsapp_jid_sync import resolve_and_save_whatsapp_jid

    pessoas = (
        db.query(Pessoa)
        .filter(Pessoa.telefone.isnot(None), Pessoa.telefone != "")
        .all()
    )
    resolved = 0
    failed = 0
    client = _client()
    for pessoa in pessoas:
        jid = resolve_and_save_whatsapp_jid(
            db, pessoa.id, pessoa.telefone, client=client
        )
        if jid:
            resolved += 1
        else:
            failed += 1

    return {
        "total": len(pessoas),
        "resolved": resolved,
        "failed": failed,
        "message": f"JIDs resolvidos: {resolved} de {len(pessoas)}",
    }


@router.post("/notificacoes/diaria/{diaria_id}/whatsapp")
def notificar_diaria_whatsapp(
    diaria_id: int,
    db: Session = Depends(get_db),
    current_user: Pessoa = Depends(require_admin()),
):
    """Reenvio manual de notificação WhatsApp para uma diária."""
    if not settings.WHATSAPP_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="WhatsApp está desabilitado (WHATSAPP_ENABLED=false)",
        )

    service = WhatsAppNotificationService(db)
    try:
        return service.notify_diaria(diaria_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except WhatsAppClientError as exc:
        raise HTTPException(
            status_code=exc.status_code or status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
