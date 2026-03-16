from rest_framework import serializers
from .models import Signal


class SignalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signal
        fields = [
            "id",
            "response_time_ms",
            "error_rate_percent",
            "downtime_minutes",
            "severity",
            "risk_score",
            "created_at",
        ]
        read_only_fields = ["id", "risk_score", "created_at"]