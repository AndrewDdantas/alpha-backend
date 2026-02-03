"""
Service para envio de emails.

Para desenvolvimento, os emails são apenas logados no console.
Para produção, integrar com serviço de email real (SendGrid, AWS SES, etc.)
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EmailService:
    """Service para envio de emails."""

    def __init__(self):
        self.from_email = os.getenv("EMAIL_FROM", "noreply@alpha.com")
        self.base_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        self.enabled = os.getenv("EMAIL_ENABLED", "false").lower() == "true"

    def enviar_email_reset_senha(self, email: str, nome: str, token: str) -> bool:
        """
        Envia email com link para redefinir senha.
        
        Args:
            email: Email do destinatário
            nome: Nome do destinatário
            token: Token de reset de senha
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        reset_link = f"{self.base_url}/#/redefinir-senha/{token}"
        
        subject = "Recuperação de Senha - Alpha"
        body = f"""
        Olá {nome},

        Recebemos uma solicitação para redefinir a senha da sua conta.

        Para criar uma nova senha, clique no link abaixo:
        {reset_link}

        Este link é válido por 1 hora.

        Se você não solicitou a redefinição de senha, ignore este email.
        Sua senha permanecerá inalterada.

        Atenciosamente,
        Equipe Alpha
        """

        # Em desenvolvimento, apenas loga no console
        if not self.enabled:
            logger.info("=" * 60)
            logger.info("📧 EMAIL DE RECUPERAÇÃO DE SENHA")
            logger.info("=" * 60)
            logger.info(f"Para: {email}")
            logger.info(f"Assunto: {subject}")
            logger.info(f"Link de reset: {reset_link}")
            logger.info("=" * 60)
            print("\n" + "=" * 60)
            print("📧 EMAIL DE RECUPERAÇÃO DE SENHA")
            print("=" * 60)
            print(f"Para: {email}")
            print(f"Nome: {nome}")
            print(f"Link de reset: {reset_link}")
            print("=" * 60 + "\n")
            return True

        # TODO: Implementar envio real de email em produção
        # Exemplo com SendGrid:
        # try:
        #     sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        #     message = Mail(
        #         from_email=self.from_email,
        #         to_emails=email,
        #         subject=subject,
        #         html_content=body
        #     )
        #     response = sg.send(message)
        #     return response.status_code == 202
        # except Exception as e:
        #     logger.error(f"Erro ao enviar email: {e}")
        #     return False

        return True

    def enviar_email_confirmacao_reset(self, email: str, nome: str) -> bool:
        """
        Envia email confirmando que a senha foi redefinida.
        
        Args:
            email: Email do destinatário
            nome: Nome do destinatário
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        subject = "Senha Redefinida - Alpha"
        body = f"""
        Olá {nome},

        Sua senha foi redefinida com sucesso.

        Se você não fez esta alteração, entre em contato conosco imediatamente.

        Atenciosamente,
        Equipe Alpha
        """

        # Em desenvolvimento, apenas loga no console
        if not self.enabled:
            logger.info(f"📧 Email de confirmação enviado para {email}")
            print(f"\n📧 Email de confirmação de reset enviado para {email}\n")
            return True

        # TODO: Implementar envio real de email em produção
        return True


# Singleton
email_service = EmailService()
