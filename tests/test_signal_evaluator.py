import pytest
from companies.models import Company
from signals.models import Signal
from signals.services.evaluator import evaluate_signal

@pytest.mark.django_db
def test_signal_severity_and_risk():
    company = Company.objects.create(
        name="TestCo",
        industry="Tech",
        size=50,
        sla_response_time_ms=500,
        sla_error_rate_percent=1.0,
        sla_downtime_minutes=2,
    )

    signal = Signal.objects.create(
        company=company,
        response_time_ms=800,      # MUHIM
        error_rate_percent=0.5,
        downtime_minutes=0,
    )

    evaluate_signal(signal)
    signal.refresh_from_db()

    assert signal.severity == "high"
    assert signal.risk_score > 0