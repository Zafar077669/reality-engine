from datetime import timedelta
from django.utils import timezone
from django.db import transaction

from incidents.models import Incident
from incidents.services.incident_updater import update_existing_incident
from incidents.services.assignment_engine import auto_assign_incident
from incidents.tasks import check_incident_escalation


INCIDENT_REOPEN_COOLDOWN_MINUTES = 30


@transaction.atomic
def route_signal_to_incident(signal):
    """
    Enterprise-grade incident routing logic.

    Flow:
    1. Reuse OPEN / INVESTIGATING incident
    2. If recently resolved (cooldown), reuse it
    3. Otherwise create NEW incident + auto-assign + schedule escalation
    """

    now = timezone.now()

    # 1️⃣ ACTIVE INCIDENT (OPEN / INVESTIGATING)
    active_incident = (
        Incident.objects
        .select_for_update()
        .filter(
            company=signal.company,
            infra_agent=signal.infra_agent,
            status__in=[
                Incident.STATUS_OPEN,
                Incident.STATUS_INVESTIGATING,
            ],
        )
        .order_by("-opened_at")
        .first()
    )

    if active_incident:
        update_existing_incident(
            incident=active_incident,
            signal=signal,
        )

        signal.incident = active_incident
        signal.save(update_fields=["incident"])
        return active_incident

    # 2️⃣ RECENTLY RESOLVED (cooldown protection)
    recent_resolved = (
        Incident.objects
        .select_for_update()
        .filter(
            company=signal.company,
            infra_agent=signal.infra_agent,
            status=Incident.STATUS_RESOLVED,
            resolved_at__gte=now - timedelta(
                minutes=INCIDENT_REOPEN_COOLDOWN_MINUTES
            ),
        )
        .order_by("-resolved_at")
        .first()
    )

    if recent_resolved:
        update_existing_incident(
            incident=recent_resolved,
            signal=signal,
        )

        signal.incident = recent_resolved
        signal.save(update_fields=["incident"])
        return recent_resolved

    # 3️⃣ CREATE NEW INCIDENT
    new_incident = Incident.objects.create(
        company=signal.company,
        infra_agent=signal.infra_agent,
        status=Incident.STATUS_OPEN,
    )

    # 🔵 AUTO ASSIGN (ONLY FOR NEW INCIDENT)
    auto_assign_incident(new_incident)

    signal.incident = new_incident
    signal.save(update_fields=["incident"])

    # 🔥 ESCALATION AUTO-SCHEDULING (PRODUCTION SAFE)
    # Uses company SLA if exists, fallback = 5 minutes
    sla_minutes = getattr(signal.company, "sla_ack_minutes", 5)

    check_incident_escalation.apply_async(
        args=[new_incident.id],
        countdown=sla_minutes * 60
    )

    return new_incident