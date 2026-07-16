"""Sincroniza whatsapp_jid das pessoas via Baileys onWhatsApp."""
from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.pessoa import Pessoa
from app.services.whatsapp_client import WhatsAppClient, WhatsAppClientError

logger = logging.getLogger(__name__)


def resolve_and_save_whatsapp_jid(
    db: Session,
    pessoa_id: int,
    telefone: Optional[str] = None,
    client: Optional[WhatsAppClient] = None,
) -> Optional[str]:
    """
    Resolve o JID WhatsApp do telefone e grava em pessoa.whatsapp_jid.
    Retorna o JID ou None se não encontrado / serviço indisponível.
    """
    if not settings.WHATSAPP_ENABLED:
        return None

    pessoa = db.query(Pessoa).filter(Pessoa.id == pessoa_id).first()
    if not pessoa:
        return None

    phone = telefone if telefone is not None else pessoa.telefone
    if not phone:
        pessoa.whatsapp_jid = None
        db.commit()
        return None

    wa = client or WhatsAppClient()
    try:
        payload = wa.resolve_numbers([phone])
    except WhatsAppClientError as exc:
        logger.warning(
            "Não foi possível resolver WhatsApp da pessoa %s: %s",
            pessoa_id,
            exc,
        )
        return None

    results = payload.get("results") or []
    match = next(
        (r for r in results if r.get("exists") and r.get("jid")),
        None,
    )
    jid = match.get("jid") if match else None
    pessoa.whatsapp_jid = jid
    db.commit()
    db.refresh(pessoa)

    if jid:
        logger.info("whatsapp_jid atualizado pessoa=%s jid=%s", pessoa_id, jid)
    else:
        logger.info(
            "Telefone da pessoa %s não encontrado no WhatsApp", pessoa_id
        )
    return jid


def sync_whatsapp_jid_background(pessoa_id: int) -> None:
    """Background task: abre sessão e resolve JID."""
    from app.db.session import SessionLocal

    if not settings.WHATSAPP_ENABLED:
        return

    db = SessionLocal()
    try:
        resolve_and_save_whatsapp_jid(db, pessoa_id)
    except Exception:
        logger.exception(
            "Erro ao sincronizar whatsapp_jid da pessoa %s", pessoa_id
        )
    finally:
        db.close()
