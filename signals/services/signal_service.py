from signals.models import Signal
from audit.services import create_audit_log


def create_signal_with_audit(
    *,
    company,
    signal_type,
    severity,
    metadata=None,
    user=None,
):
    """
    Signal yaratish + audit log
    """

    signal = Signal.objects.create(
        company=company,
        signal_type=signal_type,
        severity=severity,
        metadata=metadata or {},
    )

    create_audit_log(
        user=user,
        company=company,
        action="signal_detected",
        object_type="Signal",
        object_id=signal.id,
        metadata={
            "signal_type": signal_type,
            "severity": severity,
        },
    )

    return signal
