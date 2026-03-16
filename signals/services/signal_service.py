from signals.models import Signal
from audit.services import create_audit_log

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


# ============================================================
# REALTIME BROADCAST
# ============================================================

def broadcast_signal(signal):
    """
    Sends realtime signal update to WebSocket clients
    """

    channel_layer = get_channel_layer()

    if not channel_layer:
        return

    async_to_sync(channel_layer.group_send)(
        "signals_stream",
        {
            "type": "signal_update",
            "data": {
                "id": signal.id,
                "signal_type": signal.signal_type,
                "severity": signal.severity,
                "metadata": signal.metadata,
            },
        },
    )


# ============================================================
# CREATE SIGNAL + AUDIT + REALTIME STREAM
# ============================================================

def create_signal_with_audit(
    *,
    company,
    signal_type,
    severity,
    metadata=None,
    user=None,
):
    """
    Signal yaratish + audit log + realtime broadcast
    """

    signal = Signal.objects.create(
        company=company,
        signal_type=signal_type,
        severity=severity,
        metadata=metadata or {},
    )

    # Audit log
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

    # Realtime WebSocket broadcast
    broadcast_signal(signal)

    return signal