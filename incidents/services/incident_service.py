from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone

from audit.models import AuditLog
from companies.models import CompanyMembership
from companies.services import PermissionService
from incidents.tasks import check_incident_escalation


class IncidentService:

    # ============================
    # ASSIGN INCIDENT
    # ============================

    @staticmethod
    @transaction.atomic
    def assign_incident(actor, incident, engineer_user):

        if incident.status == "resolved":
            raise PermissionDenied("Cannot assign resolved incident")

        # Only Admin/Owner can assign
        PermissionService.require_admin_or_owner(actor, incident.company)

        # Assigned user must be Engineer
        membership = CompanyMembership.objects.filter(
            user=engineer_user,
            company=incident.company,
            role=CompanyMembership.Role.ENGINEER
        ).first()

        if not membership:
            raise PermissionDenied("Can assign only to Engineer")

        # Assign engineer
        incident.assigned_to = engineer_user
        incident.escalation_level = 0

        incident.save(update_fields=[
            "assigned_to",
            "escalation_level",
        ])

        # Schedule escalation check (5 min)
        check_incident_escalation.apply_async(
            args=[incident.id],
            countdown=300
        )

        AuditLog.objects.create(
            user=actor,
            company=incident.company,
            action="incident_assigned",
            object_type="incident",
            object_id=incident.id,
        )

        return incident

    # ============================
    # RESOLVE INCIDENT
    # ============================

    @staticmethod
    @transaction.atomic
    def resolve_incident(actor, incident):

        if incident.status == "resolved":
            raise PermissionDenied("Incident already resolved")

        PermissionService.require_admin_or_owner(actor, incident.company)

        incident.mark_resolved()

        AuditLog.objects.create(
            user=actor,
            company=incident.company,
            action="incident_resolved",
            object_type="incident",
            object_id=incident.id,
        )

        return incident

    # ============================
    # ACK INCIDENT
    # ============================

    @staticmethod
    @transaction.atomic
    def acknowledge_incident(actor, incident):

        if incident.status == "resolved":
            raise PermissionDenied("Cannot ACK resolved incident")

        if incident.acknowledged_at is not None:
            raise PermissionDenied("Incident already acknowledged")

        membership = PermissionService.get_membership(actor, incident.company)

        # Engineer, Admin yoki Owner ACK qila oladi
        if membership.role not in [
            CompanyMembership.Role.ENGINEER,
            CompanyMembership.Role.ADMIN,
            CompanyMembership.Role.OWNER,
        ]:
            raise PermissionDenied("Not allowed to ACK this incident")

        # ACK
        incident.acknowledged_at = timezone.now()
        incident.escalation_level = 0

        incident.save(update_fields=[
            "acknowledged_at",
            "escalation_level",
        ])

        AuditLog.objects.create(
            user=actor,
            company=incident.company,
            action="incident_acknowledged",
            object_type="incident",
            object_id=incident.id,
        )

        return incident