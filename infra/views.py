from datetime import timedelta
import logging

from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from infra.models import InfraAgent, InfraMetricHistory
from signals.models import Signal
from signals.services.infra_evaluator import evaluate_infra_metrics
from alerts.services.alert_dispatcher import dispatch_alert
from incidents.models import Incident

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


logger = logging.getLogger(__name__)


# ==========================================================
# 1️⃣ HEARTBEAT (Agent → Backend)
# ==========================================================

class InfraHeartbeatAPIView(APIView):
    """
    Receives heartbeat from infra agents.
    Auth: API key via Authorization header.
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        try:

            # 🔐 API KEY AUTH
            api_key = request.headers.get("Authorization")

            if not api_key:
                return Response(
                    {"error": "Missing API key"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            try:
                agent = InfraAgent.objects.select_related("company").get(
                    api_key=api_key,
                    is_active=True
                )
            except InfraAgent.DoesNotExist:
                return Response(
                    {"error": "Invalid API key"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # 📊 METRICS PAYLOAD
            try:
                cpu = float(request.data.get("cpu_percent", 0))
                ram = float(request.data.get("ram_percent", 0))
                disk = float(request.data.get("disk_percent", 0))
            except (TypeError, ValueError):
                return Response(
                    {"error": "Invalid metric values"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ❤️ UPDATE HEARTBEAT
            agent.last_seen_at = timezone.now()
            agent.save(update_fields=["last_seen_at"])

            # 📈 STORE METRICS HISTORY
            InfraMetricHistory.objects.bulk_create([
                InfraMetricHistory(
                    infra_agent=agent,
                    company=agent.company,
                    metric=InfraMetricHistory.METRIC_CPU,
                    value=cpu,
                ),
                InfraMetricHistory(
                    infra_agent=agent,
                    company=agent.company,
                    metric=InfraMetricHistory.METRIC_RAM,
                    value=ram,
                ),
                InfraMetricHistory(
                    infra_agent=agent,
                    company=agent.company,
                    metric=InfraMetricHistory.METRIC_DISK,
                    value=disk,
                ),
            ])

            # 🔥 REALTIME METRICS BROADCAST (WebSocket)
            try:

                channel_layer = get_channel_layer()

                if channel_layer:
                    async_to_sync(channel_layer.group_send)(
                        "metrics_stream",
                        {
                            "type": "send_metric",
                            "data": {
                                "cpu": cpu,
                                "ram": ram,
                                "disk": disk,
                            },
                        }
                    )

            except Exception as ws_error:

                logger.warning(
                    "Metrics WebSocket broadcast failed: %s",
                    ws_error,
                )

            # 🧠 SIGNAL ENGINE
            try:

                signal = evaluate_infra_metrics(
                    company=agent.company,
                    infra_agent=agent,
                    cpu=cpu,
                    ram=ram,
                    disk=disk,
                )

                # 🚨 ALERT ENGINE
                if signal:
                    dispatch_alert(signal)

            except Exception as signal_error:

                logger.error(
                    "Signal evaluation failed: %s",
                    signal_error,
                )

            return Response(
                {"status": "ok"},
                status=status.HTTP_200_OK
            )

        except Exception:

            logger.exception("Heartbeat processing error")

            return Response(
                {
                    "error": "internal_error",
                    "message": "Unexpected error occurred"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==========================================================
# 2️⃣ METRIC HISTORY (Charts API)
# ==========================================================

class InfraMetricHistoryAPIView(APIView):
    """
    Returns last 24h metric history for an agent.
    Used by frontend charts.
    """

    permission_classes = [AllowAny]

    def get(self, request, agent_id):

        history = (
            InfraMetricHistory.objects
            .filter(
                infra_agent_id=agent_id,
                created_at__gte=timezone.now() - timedelta(hours=24)
            )
            .order_by("created_at")
        )

        data = [
            {
                "metric": h.metric,
                "value": h.value,
                "created_at": h.created_at,
            }
            for h in history
        ]

        return Response(data)


# ==========================================================
# 3️⃣ INCIDENT OVERLAY (Chart markers)
# ==========================================================

class AgentIncidentOverlayAPIView(APIView):
    """
    Returns incidents for given agent (last 24h).
    Used for chart markers.
    """

    permission_classes = [AllowAny]

    def get(self, request, agent_id):

        incidents = (
            Incident.objects
            .filter(
                infra_agent_id=agent_id,
                created_at__gte=timezone.now() - timedelta(hours=24)
            )
            .order_by("created_at")
        )

        data = [
            {
                "incident_id": i.id,
                "status": i.status,
                "created_at": i.created_at,
            }
            for i in incidents
        ]

        return Response(data)


# ==========================================================
# 4️⃣ SERVERS STATUS (Infrastructure Monitoring)
# ==========================================================

class InfraServersStatusAPIView(APIView):
    """
    Returns infrastructure servers health status.
    Used for Servers monitoring page.
    """

    permission_classes = [AllowAny]

    def get(self, request):

        now = timezone.now()

        agents = InfraAgent.objects.select_related("company").all()

        data = []

        for agent in agents:

            if not agent.last_seen_at:

                status_value = "critical"

            else:

                diff = (now - agent.last_seen_at).total_seconds()

                if diff < 60:
                    status_value = "healthy"

                elif diff < 180:
                    status_value = "warning"

                else:
                    status_value = "critical"

            data.append({
                "id": agent.id,
                "name": agent.name,
                "company": agent.company.name,
                "last_seen_at": agent.last_seen_at,
                "status": status_value,
            })

        return Response(data)


# ==========================================================
# 5️⃣ SERVER DETAIL PAGE (Deep Monitoring)
# ==========================================================

class InfraServerDetailAPIView(APIView):
    """
    Detailed information about a single server.
    """

    permission_classes = [AllowAny]

    def get(self, request, agent_id):

        try:

            agent = InfraAgent.objects.select_related("company").get(
                id=agent_id
            )

        except InfraAgent.DoesNotExist:

            return Response(
                {"error": "Server not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Last metrics
        metrics = (
            InfraMetricHistory.objects
            .filter(infra_agent=agent)
            .order_by("-created_at")[:20]
        )

        metrics_data = [
            {
                "metric": m.metric,
                "value": m.value,
                "created_at": m.created_at
            }
            for m in metrics
        ]

        # Signals
        signals = (
            Signal.objects
            .filter(infra_agent=agent)
            .order_by("-created_at")[:10]
        )

        signals_data = [
            {
                "id": s.id,
                "severity": s.severity,
                "metric": s.metric,
                "value": s.metric_value,
                "created_at": s.created_at
            }
            for s in signals
        ]

        # Incidents
        incidents = (
            Incident.objects
            .filter(infra_agent=agent)
            .order_by("-created_at")[:10]
        )

        incidents_data = [
            {
                "id": i.id,
                "status": i.status,
                "created_at": i.created_at
            }
            for i in incidents
        ]

        return Response({

            "server": {
                "id": agent.id,
                "name": agent.name,
                "company": agent.company.name,
                "last_seen_at": agent.last_seen_at,
            },

            "metrics": metrics_data,
            "signals": signals_data,
            "incidents": incidents_data,

        })