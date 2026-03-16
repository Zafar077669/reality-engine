from django.db import models
from django.conf import settings


class AuditLog(models.Model):

    ACTION_CHOICES = [
        # Auth
        ("login", "Login"),
        ("logout", "Logout"),

        # CRUD
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),

        # System
        ("signal_generated", "Signal Generated"),
        ("incident_assigned", "Incident Assigned"),
        ("incident_resolved", "Incident Resolved"),
        ("escalation_triggered", "Escalation Triggered"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs"
    )

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs"
    )

    action = models.CharField(max_length=50, choices=ACTION_CHOICES)

    object_type = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField(null=True, blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company"]),
            models.Index(fields=["user"]),
            models.Index(fields=["action"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.action} | {self.object_type} | {self.user}"