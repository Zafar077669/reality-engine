from notifications.services.email import EmailNotifier
from notifications.services.webhook import WebhookNotifier
from notifications.types import NotificationPayload


class NotificationDispatcher:
    def __init__(self):
        self.email = EmailNotifier()
        self.webhook = WebhookNotifier()

    def dispatch(self, payload: NotificationPayload):
        # ❗ POLICY
        if payload.severity.lower() not in {"high", "critical"}:
            return

        self.email.send(payload)
        self.webhook.send(payload)