from notifications.services.dispatcher import NotificationDispatcher
from notifications.types import NotificationPayload
from notifications.models import NotificationLog


class NotificationService:
    def __init__(self):
        self.dispatcher = NotificationDispatcher()

    def notify(self, signal):
        if signal.severity.lower() not in {"high", "critical"}:
            return

        # Idempotency check
        already_sent = NotificationLog.objects.filter(
            signal_id=signal.id
        ).exists()

        if already_sent:
            return

        payload = NotificationPayload(
            company_id=signal.company_id,
            signal_id=signal.id,
            severity=signal.severity,
            message="Signal threshold breached",
            meta={
                "response_time": signal.response_time_ms,
                "risk_score": signal.risk_score,
            },
        )

        self.dispatcher.dispatch(payload)

        # Audit log (2 channel yozamiz)
        NotificationLog.objects.create(
            company_id=signal.company_id,
            signal_id=signal.id,
            severity=signal.severity,
            channel="email",
        )

        NotificationLog.objects.create(
            company_id=signal.company_id,
            signal_id=signal.id,
            severity=signal.severity,
            channel="webhook",
        )