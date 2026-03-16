from rest_framework import serializers
from infra.models import InfraAgent


class InfraAgentSerializer(serializers.ModelSerializer):

    health_score = serializers.SerializerMethodField()

    class Meta:
        model = InfraAgent
        fields = "__all__"

    def get_health_score(self, obj):
        return obj.health_score