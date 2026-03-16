import secrets
from django.db import models
from django.utils import timezone
from companies.models import Company


class InfraAgent(models.Model):
    """
    Lightweight infrastructure agent.
    Each agent represents ONE machine / node.
    Authenticates via secure API key.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="infra_agents"
    )

    name = models.CharField(
        max_length=100,
        help_text="Human-readable agent name (e.g. prod-web-1, local-dev)"
    )

    api_key = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
        help_text="Auto-generated secure API key for agent authentication"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Disable agent without deleting it"
    )

    last_seen_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last successful heartbeat timestamp"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["api_key"]),
            models.Index(fields=["company", "is_active"]),
        ]

    def save(self, *args, **kwargs):
        # 🔐 Generate API key only once
        if not self.api_key:
            self.api_key = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def mark_seen(self):
        """Update heartbeat timestamp"""
        self.last_seen_at = timezone.now()
        self.save(update_fields=["last_seen_at"])

    # ==========================================================
    # 🔥 Infrastructure Health Score (NEW – SAFE, NO MIGRATION)
    # ==========================================================

    @property
    def health_score(self):
        """
        Calculates infrastructure health score (0-100)
        based on latest metrics and active incidents.
        """
        from infra.services.health_score import calculate_agent_health
        return calculate_agent_health(self)

    def __str__(self):
        return f"{self.company.name} | {self.name}"


# ==========================================================
# 🔥 InfraMetricHistory (Observability Layer)
# ==========================================================

class InfraMetricHistory(models.Model):
    """
    Stores time-series infrastructure metrics (30s resolution).
    Enables observability dashboards & historical analysis.
    """

    METRIC_CPU = "cpu"
    METRIC_RAM = "ram"
    METRIC_DISK = "disk"

    METRIC_CHOICES = [
        (METRIC_CPU, "CPU"),
        (METRIC_RAM, "RAM"),
        (METRIC_DISK, "Disk"),
    ]

    infra_agent = models.ForeignKey(
        InfraAgent,
        on_delete=models.CASCADE,
        related_name="metric_history",
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="metric_history",
    )

    metric = models.CharField(
        max_length=20,
        choices=METRIC_CHOICES,
        db_index=True,
    )

    value = models.FloatField()

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["infra_agent", "metric", "created_at"]),
            models.Index(fields=["company", "metric", "created_at"]),
        ]

    def __str__(self):
        return f"{self.infra_agent.name} | {self.metric} | {self.value}"