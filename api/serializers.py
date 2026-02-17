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
            "signal_type",
            "severity",
            "explanation",
            "predicted_impact",
            "detected_at",
        ]
        read_only_fields = ["id", "detected_at"]
