from django.db import models

# Create your models here.

class NotificationLog(models.Model):
    CHANNEL_CHOICES = [
        ("email", "Email"),
        ("webhook", "Webhook"),
    ]

    company_id = models.IntegerField()
    signal_id = models.IntegerField()
    severity = models.CharField(max_length=20)

    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    status = models.CharField(max_length=20, default="sent")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["signal_id"]),
        ]