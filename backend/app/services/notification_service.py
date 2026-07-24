import asyncio
import logging
from email.mime.text import MIMEText
from typing import Protocol

logger = logging.getLogger(__name__)


class BudgetAlertNotifier(Protocol):
    async def send_budget_alert(self, recipient_email: str, message: str) -> None:
        ...


class NoopBudgetAlertNotifier:
    async def send_budget_alert(self, recipient_email: str, message: str) -> None:
        return None


class SmtpBudgetAlertNotifier:
    def __init__(self) -> None:
        from app.core.config import get_settings
        s = get_settings()
        self.host = s.smtp_host
        self.port = s.smtp_port
        self.user = s.smtp_user
        self.password = s.smtp_password
        self.from_email = s.smtp_from_email
        self.from_name = s.smtp_from_name

    async def send_budget_alert(self, recipient_email: str, message: str) -> None:
        if not self.host:
            logger.warning("SMTP not configured; skipping email to %s", recipient_email)
            return
        msg = MIMEText(message, "plain", "utf-8")
        msg["Subject"] = f"[{self.from_name}] Budget Alert"
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = recipient_email

        def _send() -> None:
            import smtplib
            with smtplib.SMTP(self.host, self.port) as server:
                if self.user:
                    server.starttls()
                    server.login(self.user, self.password)
                server.sendmail(self.from_email, [recipient_email], msg.as_string())

        try:
            await asyncio.to_thread(_send)
            logger.info("Budget alert email sent to %s", recipient_email)
        except Exception:
            logger.exception("Failed to send budget alert email to %s", recipient_email)


notifier: BudgetAlertNotifier = SmtpBudgetAlertNotifier()
