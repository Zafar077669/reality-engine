# incidents/services/assignment_engine.py

from django.db import transaction
from django.utils import timezone

from users.models import User
from incidents.models import Incident, IncidentTimeline


@transaction.atomic
def auto_assign_incident(incident: Incident):
    """
    Auto-assign incident to next available user (round-robin).
    """

    if incident.assigned_to:
        return incident

    # Company users (active only)
    users = (
        User.objects
        .filter(company=incident.company, is_active=True)
        .order_by("id")
    )

    if not users.exists():
        return incident

    # 🔁 Simple round-robin:
    # Find last assigned incident
    last_incident = (
        Incident.objects
        .filter(company=incident.company, assigned_to__isnull=False)
        .order_by("-created_at")
        .first()
    )

    if not last_incident:
        selected_user = users.first()
    else:
        user_ids = list(users.values_list("id", flat=True))
        try:
            last_index = user_ids.index(last_incident.assigned_to_id)
            next_index = (last_index + 1) % len(user_ids)
            selected_user = users.get(id=user_ids[next_index])
        except ValueError:
            selected_user = users.first()

    # Assign
    incident.assigned_to = selected_user
    incident.save(update_fields=["assigned_to"])

    # Timeline
    IncidentTimeline.objects.create(
        incident=incident,
        event_type=IncidentTimeline.EVENT_ASSIGNMENT,
        message=f"Incident auto-assigned to {selected_user.username}",
    )

    return incident