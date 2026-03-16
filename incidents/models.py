from django.db import models
from django.utils import timezone
from django.conf import settings

from companies.models import Company
from users.models import User
from infra.models import InfraAgent


class Incident(models.Model):
    """
    Core operational entity.
    Represents a real infrastructure problem.
    """

    STATUS_OPEN = "open"
    STATUS_INVESTIGATING = "investigating"
    STATUS_RESOLVED = "resolved"

    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_INVESTIGATING, "Investigating"),
        (STATUS_RESOLVED, "Resolved"),
    ]

    SEVERITY_LOW = "low"
    SEVERITY_WARNING = "warning"
    SEVERITY_CRITICAL = "critical"

    SEVERITY_CHOICES = [
        (SEVERITY_LOW, "Low"),
        (SEVERITY_WARNING, "Warning"),
        (SEVERITY_CRITICAL, "Critical"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="incidents",
    )

    infra_agent = models.ForeignKey(
        InfraAgent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incidents",
    )

    # 🔥 Incident metadata
    title = models.CharField(max_length=255, default="Infrastructure Incident")
    summary = models.TextField(null=True, blank=True)

    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default=SEVERITY_WARNING,
        db_index=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
        db_index=True,
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_incidents",
    )

    root_cause = models.TextField(
        null=True,
        blank=True,
    )

    opened_at = models.DateTimeField(auto_now_add=True)
    investigating_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # 🔒 TELEGRAM DEDUP FLAG
    telegram_notified = models.BooleanField(default=False)

    # 🔥 ACK SYSTEM
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="acknowledged_incidents",
    )

    # 🔥 ESCALATION SYSTEM
    escalation_level = models.PositiveIntegerField(default=0)
    last_escalated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-opened_at"]
        indexes = [
            models.Index(fields=["company", "status"]),
            models.Index(fields=["infra_agent", "status"]),
            models.Index(fields=["company", "acknowledged_at"]),
            models.Index(fields=["company", "escalation_level"]),
            models.Index(fields=["company", "severity"]),
        ]

    # ============================
    # Status Transitions
    # ============================

    def mark_investigating(self):
        if self.status == self.STATUS_OPEN:
            self.status = self.STATUS_INVESTIGATING
            self.investigating_at = timezone.now()
            self.save(update_fields=["status", "investigating_at"])

            self._log_event(
                IncidentTimeline.EVENT_STATUS_CHANGE,
                "Status changed to INVESTIGATING"
            )

    def mark_resolved(self, root_cause=None):
        if self.status != self.STATUS_RESOLVED:
            self.status = self.STATUS_RESOLVED
            self.resolved_at = timezone.now()

            if root_cause:
                self.root_cause = root_cause

            self.save()

            self._log_event(
                IncidentTimeline.EVENT_STATUS_CHANGE,
                "Status changed to RESOLVED"
            )

    def reopen(self):
        if self.status == self.STATUS_RESOLVED:
            self.status = self.STATUS_OPEN
            self.resolved_at = None
            self.save(update_fields=["status", "resolved_at"])

            self._log_event(
                IncidentTimeline.EVENT_STATUS_CHANGE,
                "Incident reopened"
            )

    # ============================
    # ACK Helper
    # ============================

    def acknowledge(self, user):
        if not self.acknowledged_at:
            self.acknowledged_at = timezone.now()
            self.acknowledged_by = user
            self.save(update_fields=["acknowledged_at", "acknowledged_by"])

            self._log_event(
                IncidentTimeline.EVENT_NOTE,
                f"Acknowledged by {user}"
            )

    def is_acknowledged(self):
        return self.acknowledged_at is not None

    # ============================
    # Escalation Helpers
    # ============================

    def can_escalate(self):
        return (
            self.status != self.STATUS_RESOLVED
            and self.acknowledged_at is None
        )

    def escalate(self):
        if self.can_escalate():
            self.escalation_level += 1
            self.last_escalated_at = timezone.now()

            self.save(update_fields=["escalation_level", "last_escalated_at"])

            self._log_event(
                IncidentTimeline.EVENT_NOTE,
                f"Escalated to level {self.escalation_level}"
            )

    # ============================
    # SRE Metrics
    # ============================

    @property
    def mttr_minutes(self):
        if not self.resolved_at:
            return None

        delta = self.resolved_at - self.opened_at
        return int(delta.total_seconds() / 60)

    @property
    def duration_minutes(self):
        end_time = self.resolved_at or timezone.now()
        delta = end_time - self.opened_at
        return int(delta.total_seconds() / 60)

    # ============================
    # Timeline Logging
    # ============================

    def _log_event(self, event_type, message):
        IncidentTimeline.objects.create(
            incident=self,
            event_type=event_type,
            message=message,
        )

    # ============================
    # Assignment Change Logging
    # ============================

    def save(self, *args, **kwargs):

        if self.pk:
            previous = Incident.objects.filter(pk=self.pk).first()

            if previous and previous.assigned_to != self.assigned_to:
                IncidentTimeline.objects.create(
                    incident=self,
                    event_type=IncidentTimeline.EVENT_ASSIGNMENT,
                    message=f"Assigned to {self.assigned_to}",
                )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Incident #{self.id} | {self.company.name} | {self.status.upper()}"


class IncidentTimeline(models.Model):
    """
    Stores audit trail of incident lifecycle.
    """

    EVENT_STATUS_CHANGE = "status_change"
    EVENT_ASSIGNMENT = "assignment"
    EVENT_NOTE = "note"

    EVENT_TYPES = [
        (EVENT_STATUS_CHANGE, "Status Change"),
        (EVENT_ASSIGNMENT, "Assignment"),
        (EVENT_NOTE, "Note"),
    ]

    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name="timeline_events",
    )

    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPES,
    )

    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["incident", "event_type"]),
        ]

    def __str__(self):
        return f"{self.incident} | {self.event_type}"