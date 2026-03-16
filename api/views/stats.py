from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from signals.models import Signal

class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "total_signals": Signal.objects.count(),
            "critical": Signal.objects.filter(severity="critical").count(),
            "high": Signal.objects.filter(severity="high").count(),
            "medium": Signal.objects.filter(severity="medium").count(),
            "low": Signal.objects.filter(severity="low").count(),
        })