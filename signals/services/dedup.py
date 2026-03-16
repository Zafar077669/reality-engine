from typing import Optional

from companies.models import Company
from signals.models import Signal


def existing_open_signal(
    company: Company,
    metric: Optional[str],
    severity: str
) -> bool:
    """
    Check if an OPEN signal already exists for the given
    company + metric + severity combination.

    Prevents alert storm when the same metric keeps
    violating a rule.
    """

    if metric is None:
        return False

    return Signal.objects.filter(
        company=company,
        metric=metric,
        severity=severity,
        status="open",
    ).exists()