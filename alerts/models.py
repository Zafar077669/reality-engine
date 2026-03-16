from django.db import models
from django.utils import timezone

from companies.models import Company
from users.models import User
from signals.models import Signal
from incidents.models import Incident


# ============================================================
# ALERT RULE (Metric-based Alert Configuration)
# ============================================================

class AlertRule(models.Model):

    METRIC_CHOICES = (
        ("cpu", "CPU"),
        ("ram", "RAM"),
        ("disk", "Disk"),
    )

    OPERATOR_CHOICES = (
        (">", "Greater than"),
        ("<", "Less than"),
    )

    SEVERITY_CHOICES = (
        ("critical", "Critical"),
        ("high", "High"),
        ("warning", "Warning"),
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="alert_rules"
    )

    name = models.CharField(
        max_length=200
    )

    metric = models.CharField(
        max_length=20,
        choices=METRIC_CHOICES
    )

    operator = models.CharField(
        max_length=2,
        choices=OPERATOR_CHOICES
    )

    threshold = models.FloatField()

    duration = models.IntegerField(
        default=0,
        help_text="Seconds metric must stay above threshold"
    )

    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES
    )

    is_active = models.BooleanField(default=True)

    send_telegram = models.BooleanField(default=True)
    send_email = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["company", "metric"]),
            models.Index(fields=["company", "severity"]),
            models.Index(fields=["metric", "is_active"]),
        ]

    def __str__(self):
        return f"{self.company.name} | {self.metric} {self.operator} {self.threshold}"


# ============================================================
# ALERT HISTORY (Universal Notification Log)
# ============================================================

class AlertHistory(models.Model):

    STATUS_CHOICES = (
        ("sent", "Sent"),
        ("failed", "Failed"),
        ("acked", "Acknowledged"),
    )

    CHANNEL_CHOICES = (
        ("telegram", "Telegram"),
        ("email", "Email"),
        ("slack", "Slack"),
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="alert_histories"
    )

    signal = models.ForeignKey(
        Signal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alert_histories"
    )

    incident = models.ForeignKey(
        Incident,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alert_histories"
    )

    recipient = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_alerts"
    )

    channel = models.CharField(
        max_length=20,
        choices=CHANNEL_CHOICES,
        default="telegram"
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="sent"
    )

    message = models.TextField()

    error_message = models.TextField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    acked_at = models.DateTimeField(
        null=True,
        blank=True
    )

    acknowledged_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="acknowledged_alerts"
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["company", "status"]),
            models.Index(fields=["channel", "status"]),
            models.Index(fields=["incident"]),
            models.Index(fields=["signal"]),
        ]

    # ========================================================
    # ACK METHOD
    # ========================================================

    def mark_acked(self, user: User | None = None):

        self.status = "acked"
        self.acked_at = timezone.now()
        self.acknowledged_by = user

        self.save(
            update_fields=[
                "status",
                "acked_at",
                "acknowledged_by"
            ]
        )

    def __str__(self):

        if self.incident:
            target = f"Incident {self.incident.id}"

        elif self.signal:
            target = f"Signal {self.signal.id}"

        else:
            target = "N/A"

        return f"[{self.status.upper()}] {self.channel} → {target}"