from typing import Protocol


class BudgetAlertNotifier(Protocol):
    async def send_budget_alert(self, recipient_email: str, message: str) -> None:
        ...


class NoopBudgetAlertNotifier:
    async def send_budget_alert(self, recipient_email: str, message: str) -> None:
        return None


notifier: BudgetAlertNotifier = NoopBudgetAlertNotifier()
