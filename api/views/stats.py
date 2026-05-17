from datetime import timedelta
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from signals.models import Signal
from companies.models import CompanyMembership


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        membership = CompanyMembership.objects.filter(user=request.user).select_related("company").first()

        if not membership:
            return Response({
                "total_signals": 0,
                "critical": 0,
                "warning": 0,
                "uptime": 0
            })

        company = membership.company

        #  Faqat shu company signalari
        signals = Signal.objects.filter(company=company)

        total = signals.count()
        critical = signals.filter(severity="critical").count()
        warning = signals.filter(severity="warning").count()

        # =========================
        #  REAL UPTIME (24h)
        # =========================
        now = timezone.now()
        window_start = now - timedelta(hours=24)

        recent = signals.filter(created_at__gte=window_start)

        total_events = recent.count()
        critical_events = recent.filter(severity="critical").count()

        if total_events == 0:
            uptime = 100.0 if total > 0 else 0.0
        else:
            uptime = round((1 - (critical_events / total_events)) * 100, 2)

        return Response({
            "total_signals": total,
            "critical": critical,
            "warning": warning,
            "uptime": uptime
        })