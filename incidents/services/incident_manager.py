from incidents.models import Incident


def attach_signal_to_incident(signal):
    incident = Incident.objects.filter(
        company=signal.company,
        infra_agent=signal.infra_agent,
        status__in=[
            Incident.STATUS_OPEN,
            Incident.STATUS_INVESTIGATING
        ]
    ).first()

    if not incident:
        incident = Incident.objects.create(
            company=signal.company,
            infra_agent=signal.infra_agent,
        )

    signal.incident = incident
    signal.save(update_fields=["incident"])

    return incident