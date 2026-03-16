from notifications.services.dispatcher import NotificationDispatcher
from notifications.types import NotificationPayload


def test_notification_dispatch_does_not_fail():
    payload = NotificationPayload(
        company_id=1,
        signal_id=1,
        severity="HIGH",
        message="Test alert",
        meta={},
    )

    dispatcher = NotificationDispatcher()
    dispatcher.dispatch(payload)