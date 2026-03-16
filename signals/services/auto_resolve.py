from signals.models import Signal


def resolve_signal_if_recovered(company, metric_name, value, rule):
    """
    Resolve open signals when metric returns to normal state
    according to the rule that created the signal.
    """

    open_signals = Signal.objects.filter(
        company=company,
        metric=metric_name,
        severity=rule.severity,
        status="open"
    )

    if not open_signals.exists():
        return

    recovered = False

    # Rule: metric > threshold
    if rule.operator == ">" and value <= rule.threshold:
        recovered = True

    # Rule: metric < threshold
    if rule.operator == "<" and value >= rule.threshold:
        recovered = True

    if recovered:
        open_signals.update(status="resolved")