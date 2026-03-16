from rest_framework import serializers
from events.models import Event
from signals.models import Signal


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "actor",
            "event_type",
            "timestamp",
            "metadata",
        ]
        read_only_fields = ["id"]


class SignalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signal
        fields = [
            "id",
            "company",
            "response_time_ms",
            "error_rate_percent",
            "downtime_minutes",
            "severity",
            "risk_score",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]