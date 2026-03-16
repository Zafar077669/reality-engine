from django.db import models
from django.conf import settings


class Company(models.Model):
    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=100, blank=True)
    size = models.PositiveIntegerField(help_text="Employee count")

    # 🔥 SLA Configuration
    sla_response_time_ms = models.IntegerField(default=800)
    sla_error_rate_percent = models.FloatField(default=2.0)
    sla_downtime_minutes = models.IntegerField(default=5)

    evaluation_window_minutes = models.IntegerField(default=3)

    # 🚨 ALERT DESTINATION (Telegram)
    telegram_chat_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Telegram user or group chat_id for alerts"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# 🔥 ENTERPRISE RBAC FOUNDATION
class CompanyMembership(models.Model):

    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        ENGINEER = "engineer", "Engineer"
        VIEWER = "viewer", "Viewer"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="company_memberships"
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "company")
        indexes = [
            models.Index(fields=["company"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.company.name} ({self.role})"