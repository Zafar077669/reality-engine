from signals.models import Signal
from signals.services.dedup import existing_open_signal


def create_signal_if_needed(company, metric_name, value, rule):

    if existing_open_signal(company, metric_name, rule.severity):
        return None

    return Signal.objects.create(
        company=company,
        metric=metric_name,
        metric_value=value,
        severity=rule.severity,
        source="infra",
        status="open",
    )