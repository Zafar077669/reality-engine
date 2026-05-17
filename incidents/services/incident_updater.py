from django.utils import timezone

from incidents.models import Incident, IncidentTimeline


def update_existing_incident(*, incident, signal):
    """
    Update existing incident with new signal info.
    Adds timeline event instead of opening new incident.
    """


    metric = signal.metric
    value = signal.metric_value
    severity = signal.severity.upper()

    message = (
        f"{metric.upper()} still {severity} "
        f"({value}%) — heartbeat update"
    )

    IncidentTimeline.objects.create(
        incident=incident,
        event_type=IncidentTimeline.EVENT_NOTE,
        message=message,
    )

    if not incident.infra_agent and signal.infra_agent:
        incident.infra_agent = signal.infra_agent
        incident.save(update_fields=["infra_agent"])