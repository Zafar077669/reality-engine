# signals/services/infra_evaluator.py

from datetime import timedelta
import logging

from django.utils import timezone

from signals.models import Signal
from signals.services.incident_router import route_signal_to_incident


logger = logging.getLogger(__name__)


# ==========================================================
# Threshold Configuration
# ==========================================================

CPU_WARNING = 80
CPU_CRITICAL = 90

RAM_WARNING = 85
RAM_CRITICAL = 95

DISK_WARNING = 90
DISK_CRITICAL = 97

SIGNAL_COOLDOWN_MINUTES = 2


# ==========================================================
# Public API
# ==========================================================

def evaluate_infra_metrics(
    *,
    company,
    infra_agent,
    cpu: float,
    ram: float,
    disk: float,
):
    """
    Evaluate infra metrics and create Signal if threshold breached.

    Returns:
    - Signal instance if created
    - None if no issue or cooldown active
    """

    decision = _decide_severity(cpu=cpu, ram=ram, disk=disk)

    if not decision:
        return None

    severity, metric, value = decision

    if _is_in_cooldown(
        infra_agent=infra_agent,
        metric=metric,
        severity=severity,
    ):
        return None

    signal = _create_signal(
        company=company,
        infra_agent=infra_agent,
        severity=severity,
        metric=metric,
        value=value,
    )

    # 🔥 INCIDENT ROUTING (protected)
    try:
        route_signal_to_incident(signal)
    except Exception as exc:
        logger.error(
            "Incident routing failed for signal %s: %s",
            signal.id,
            exc,
        )

    return signal


# ==========================================================
# Internal Logic
# ==========================================================

def _decide_severity(*, cpu, ram, disk):
    """
    Determine severity and metric.
    CRITICAL has higher priority than WARNING.
    """

    if cpu >= CPU_CRITICAL:
        return "critical", "cpu", cpu

    if ram >= RAM_CRITICAL:
        return "critical", "ram", ram

    if disk >= DISK_CRITICAL:
        return "critical", "disk", disk

    if cpu >= CPU_WARNING:
        return "warning", "cpu", cpu

    if ram >= RAM_WARNING:
        return "warning", "ram", ram

    if disk >= DISK_WARNING:
        return "warning", "disk", disk

    return None


def _is_in_cooldown(*, infra_agent, metric, severity):
    """
    Prevent duplicate signal spam within cooldown window.
    """

    recent_time = timezone.now() - timedelta(
        minutes=SIGNAL_COOLDOWN_MINUTES
    )

    return Signal.objects.filter(
        infra_agent=infra_agent,
        metric=metric,
        severity=severity,
        source="infra",
        created_at__gte=recent_time,
    ).exists()


def _create_signal(*, company, infra_agent, severity, metric, value):
    """
    Persist Signal in database.
    """

    return Signal.objects.create(
        company=company,
        infra_agent=infra_agent,
        severity=severity,
        metric=metric,
        metric_value=value,
        source="infra",
    )