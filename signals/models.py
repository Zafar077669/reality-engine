from django.db import models
from companies.models import Company


class Signal(models.Model):

    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("warning", "Warning"),
        ("critical", "Critical"),
    ]

    SOURCE_CHOICES = [
        ("manual", "Manual"),
        ("infra", "Infrastructure"),
        ("sla", "SLA"),
    ]

    STATUS_CHOICES = [
        ("open", "Open"),
        ("resolved", "Resolved"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="signals"
    )

    # 🔗 Incident integration
    incident = models.ForeignKey(
        "incidents.Incident",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="signals"
    )

    # 🔗 Infra agent integration
    infra_agent = models.ForeignKey(
        "infra.InfraAgent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="signals"
    )

    # 🔥 Infra metrics
    metric = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="cpu | ram | disk"
    )

    metric_value = models.FloatField(
        null=True,
        blank=True
    )

    # 🧠 SLA / Business metrics
    response_time_ms = models.IntegerField(
        null=True,
        blank=True
    )

    error_rate_percent = models.FloatField(
        default=0
    )

    downtime_minutes = models.IntegerField(
        default=0
    )

    # 🚨 Core fields
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default="low"
    )

    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default="manual"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open"
    )

    risk_score = models.FloatField(
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "metric"]),
            models.Index(fields=["company", "status"]),
            models.Index(fields=["metric", "severity"]),
        ]

    def __str__(self):
        return (
            f"{self.company.name} | "
            f"{self.severity.upper()} | "
            f"{self.source}"
        )