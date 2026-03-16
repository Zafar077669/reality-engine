from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from incidents.models import Incident, IncidentTimeline
from incidents.services.assignment_engine import auto_assign_incident
from audit.models import AuditLog


# ==============================
# LEVEL 1 ESCALATION
# ==============================

@shared_task(bind=True, max_retries=3)
def check_incident_escalation(self, incident_id):

    try:
        incident = Incident.objects.select_related("company").get(id=incident_id)
    except Incident.DoesNotExist:
        return

    if not incident.can_escalate():
        return

    escalation_deadline = incident.created_at + timedelta(
        minutes=getattr(incident.company, "sla_ack_minutes", 5)
    )

    if timezone.now() < escalation_deadline:
        return

    # Prevent duplicate
    if incident.escalation_level >= 1:
        return

    incident.escalation_level = 1
    incident.last_escalated_at = timezone.now()
    incident.save(update_fields=["escalation_level", "last_escalated_at"])

    IncidentTimeline.objects.create(
        incident=incident,
        event_type=IncidentTimeline.EVENT_NOTE,
        message="Escalation Level 1 triggered (No ACK within SLA)",
    )

    AuditLog.objects.create(
        user=None,
        company=incident.company,
        action="escalation_level_1",
        object_type="incident",
        object_id=incident.id,
    )

    # 🔥 Schedule Level 2 in 10 minutes
    check_incident_escalation_level_2.apply_async(
        args=[incident.id],
        countdown=10 * 60
    )


# ==============================
# LEVEL 2 ESCALATION
# ==============================

@shared_task(bind=True, max_retries=3)
def check_incident_escalation_level_2(self, incident_id):

    try:
        incident = Incident.objects.select_related("company").get(id=incident_id)
    except Incident.DoesNotExist:
        return

    if not incident.can_escalate():
        return

    # Only if still level 1
    if incident.escalation_level != 1:
        return

    # Ensure 15 minutes passed total
    level_2_deadline = incident.created_at + timedelta(minutes=15)

    if timezone.now() < level_2_deadline:
        return

    incident.escalation_level = 2
    incident.last_escalated_at = timezone.now()
    incident.save(update_fields=["escalation_level", "last_escalated_at"])

    # 🔁 Rotate engineer
    auto_assign_incident(incident)

    IncidentTimeline.objects.create(
        incident=incident,
        event_type=IncidentTimeline.EVENT_NOTE,
        message="Escalation Level 2 triggered (Reassigned to next engineer)",
    )

    AuditLog.objects.create(
        user=None,
        company=incident.company,
        action="escalation_level_2",
        object_type="incident",
        object_id=incident.id,
    )