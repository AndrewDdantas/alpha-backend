"""Notificações WhatsApp para diárias."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.diaria import Diaria
from app.models.enums import TipoPessoa
from app.models.pessoa import Pessoa
from app.services.whatsapp_client import WhatsAppClient, WhatsAppClientError
from app.services.whatsapp_jid_sync import resolve_and_save_whatsapp_jid

logger = logging.getLogger(__name__)


class WhatsAppNotificationService:
    """Monta destinatários e dispara mensagens de diária."""

    def __init__(self, db: Session, client: Optional[WhatsAppClient] = None):
        self.db = db
        self.client = client or WhatsAppClient()

    def list_colaboradores_com_telefone(self) -> List[Pessoa]:
        return (
            self.db.query(Pessoa)
            .filter(
                Pessoa.tipo_pessoa == TipoPessoa.COLABORADOR,
                Pessoa.ativo.is_(True),
                Pessoa.bloqueado.is_(False),
                Pessoa.telefone.isnot(None),
                Pessoa.telefone != "",
            )
            .all()
        )

    def build_diaria_message(self, diaria: Diaria) -> str:
        data_str = diaria.data.strftime("%d/%m/%Y") if diaria.data else "-"
        inicio = (
            diaria.horario_inicio.strftime("%H:%M")
            if diaria.horario_inicio
            else "--:--"
        )
        fim = (
            diaria.horario_fim.strftime("%H:%M")
            if diaria.horario_fim
            else "--:--"
        )
        local = diaria.local or "A definir"
        empresa_nome = diaria.empresa.nome if diaria.empresa else "-"

        return (
            "Nova diária disponível!\n"
            f"*{diaria.titulo}*\n"
            f"Data: {data_str} | {inicio} - {fim}\n"
            f"Local: {local}\n"
            f"Vagas: {diaria.vagas}\n"
            f"Empresa: {empresa_nome}\n"
            "Acesse o app Alpha para se inscrever."
        )

    def _ensure_jids(self, colaboradores: List[Pessoa]) -> List[str]:
        """Garante whatsapp_jid (resolve via onWhatsApp se faltar) e retorna JIDs."""
        jids: List[str] = []
        missing_phones: List[str] = []
        missing_pessoas: List[Pessoa] = []

        for pessoa in colaboradores:
            if pessoa.whatsapp_jid:
                jids.append(pessoa.whatsapp_jid)
            elif pessoa.telefone:
                missing_phones.append(pessoa.telefone)
                missing_pessoas.append(pessoa)

        if not missing_phones:
            return jids

        try:
            payload = self.client.resolve_numbers(missing_phones)
        except WhatsAppClientError as exc:
            logger.error("Falha ao resolver JIDs em lote: %s", exc)
            # Fallback: envia pelos telefones (serviço resolve no send)
            return jids

        results = payload.get("results") or []
        by_phone = {
            (r.get("number") or ""): r for r in results if isinstance(r, dict)
        }

        for pessoa in missing_pessoas:
            match = by_phone.get(pessoa.telefone or "")
            jid = match.get("jid") if match and match.get("exists") else None
            if jid:
                pessoa.whatsapp_jid = jid
                jids.append(jid)
            else:
                # tenta individual (variantes BR)
                resolved = resolve_and_save_whatsapp_jid(
                    self.db, pessoa.id, pessoa.telefone, client=self.client
                )
                if resolved:
                    jids.append(resolved)

        self.db.commit()
        return jids

    def notify_diaria(self, diaria_id: int) -> Dict[str, Any]:
        if not settings.WHATSAPP_ENABLED:
            return {
                "sent": 0,
                "failed": [],
                "recipients": 0,
                "message": "WhatsApp desabilitado (WHATSAPP_ENABLED=false)",
                "disabled": True,
            }

        diaria = (
            self.db.query(Diaria)
            .filter(Diaria.id == diaria_id)
            .first()
        )
        if not diaria:
            raise ValueError("Diária não encontrada")

        _ = diaria.empresa

        colaboradores = self.list_colaboradores_com_telefone()
        if not colaboradores:
            return {
                "sent": 0,
                "failed": [],
                "recipients": 0,
                "message": "Nenhum colaborador ativo com telefone cadastrado",
            }

        jids = self._ensure_jids(colaboradores)
        text = self.build_diaria_message(diaria)

        if not jids:
            # Último recurso: envia pelos telefones e deixa o serviço resolver
            numbers = [p.telefone for p in colaboradores if p.telefone]
            try:
                result = self.client.send_messages(numbers, text)
            except WhatsAppClientError as exc:
                logger.error("Falha ao notificar diária %s: %s", diaria_id, exc)
                raise
        else:
            try:
                result = self.client.send_to_jids(jids, text)
            except WhatsAppClientError as exc:
                logger.error("Falha ao notificar diária %s: %s", diaria_id, exc)
                raise

        sent = int(result.get("sent") or 0)
        failed = result.get("failed") or []
        return {
            "sent": sent,
            "failed": failed,
            "recipients": len(jids) if jids else len(colaboradores),
            "message": (
                f"Notificação enviada: {sent} de "
                f"{len(jids) if jids else len(colaboradores)}"
            ),
        }


def notify_diaria_background(diaria_id: int) -> None:
    """Task de background: abre sessão própria e notifica."""
    from app.db.session import SessionLocal

    if not settings.WHATSAPP_ENABLED:
        logger.info(
            "WhatsApp desabilitado; pulando notificação da diária %s", diaria_id
        )
        return

    db = SessionLocal()
    try:
        service = WhatsAppNotificationService(db)
        result = service.notify_diaria(diaria_id)
        logger.info(
            "Notificação WhatsApp diária %s: %s",
            diaria_id,
            result.get("message"),
        )
    except Exception as exc:
        logger.exception(
            "Erro na notificação WhatsApp da diária %s: %s", diaria_id, exc
        )
    finally:
        db.close()
