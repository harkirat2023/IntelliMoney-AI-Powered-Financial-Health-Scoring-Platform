import logging
from typing import Protocol

logger = logging.getLogger(__name__)


class BudgetAlertNotifier(Protocol):
    async def send_budget_alert(self, recipient_email: str, message: str) -> None:
        ...


class NoopBudgetAlertNotifier:
    async def send_budget_alert(self, recipient_email: str, message: str) -> None:
        return None


# IntelliMoney notifications are in-app alert logic only (see PRD §23).
# Email delivery was intentionally removed; alerts are persisted and
# surfaced through the alerts/dashboard-notifications endpoints.
notifier: BudgetAlertNotifier = NoopBudgetAlertNotifier()
