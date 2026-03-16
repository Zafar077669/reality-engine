import pytest
from companies.models import Company
from signals.models import Signal
from notifications.services.service import NotificationService
from notifications.models import NotificationLog


@pytest.mark.django_db
def test_notification_created_for_high_severity():
    company = Company.objects.create(name="TestCo", size=10)

    signal = Signal.objects.create(
        company=company,
        response_time_ms=100,
        severity="high",
    )

    NotificationService().notify(signal)

    logs = NotificationLog.objects.filter(signal_id=signal.id)

    assert logs.count() == 2