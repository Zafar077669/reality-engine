from typing import List

from companies.models import Company
from alerts.models import AlertRule

from signals.services.signal_creator import create_signal_if_needed
from signals.services.auto_resolve import resolve_signal_if_recovered


# ============================================================
# OPERATOR COMPARISON
# ============================================================

def _compare(operator: str, value: float, threshold: float) -> bool:
    """
    Evaluate metric value against threshold using rule operator.
    """

    if operator == ">":
        return value > threshold

    if operator == "<":
        return value < threshold

    return False


# ============================================================
# RULE EVALUATION (optional helper)
# ============================================================

def evaluate_rules(
    company: Company,
    metric_name: str,
    value: float
) -> List[AlertRule]:
    """
    Return rules that are violated by the metric.
    """

    rules = AlertRule.objects.filter(
        company=company,
        metric=metric_name,
        is_active=True,
    )

    matched_rules: List[AlertRule] = []

    for rule in rules:
        try:
            if _compare(rule.operator, value, rule.threshold):
                matched_rules.append(rule)
        except Exception:
            continue

    return matched_rules


# ============================================================
# METRIC PROCESSING ENTRYPOINT
# ============================================================

def process_metric(
    company: Company,
    metric_name: str,
    value: float
) -> None:
    """
    Main entrypoint for metric processing.

    Pipeline
    --------
    metric received
        ↓
    resolve signals if recovered
        ↓
    check rule violations
        ↓
    create signal if needed
    """

    rules = AlertRule.objects.filter(
        company=company,
        metric=metric_name,
        is_active=True,
    )

    if not rules.exists():
        return

    for rule in rules:

        # 1️⃣ resolve signal if metric returned to normal
        resolve_signal_if_recovered(
            company=company,
            metric_name=metric_name,
            value=value,
            rule=rule,
        )

        # 2️⃣ if rule violated → create signal
        if _compare(rule.operator, value, rule.threshold):

            try:
                create_signal_if_needed(
                    company=company,
                    metric_name=metric_name,
                    value=value,
                    rule=rule,
                )
            except Exception:
                continue