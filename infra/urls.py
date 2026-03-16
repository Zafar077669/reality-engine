from django.urls import path

from .views import (
    InfraHeartbeatAPIView,
    InfraMetricHistoryAPIView,
    AgentIncidentOverlayAPIView,
    InfraServersStatusAPIView,
    InfraServerDetailAPIView,
)


urlpatterns = [

    # ======================================================
    # 1️⃣ HEARTBEAT (Infra Agent → Backend)
    # ======================================================
    path(
        "heartbeat/",
        InfraHeartbeatAPIView.as_view(),
        name="infra-heartbeat",
    ),

    # ======================================================
    # 2️⃣ METRICS HISTORY (Charts API)
    # ======================================================
    path(
        "metrics/<int:agent_id>/history/",
        InfraMetricHistoryAPIView.as_view(),
        name="infra-metrics-history",
    ),

    # ======================================================
    # 3️⃣ INCIDENT OVERLAY (Chart markers)
    # ======================================================
    path(
        "metrics/<int:agent_id>/incidents/",
        AgentIncidentOverlayAPIView.as_view(),
        name="infra-metrics-incidents",
    ),

    # ======================================================
    # 4️⃣ SERVERS STATUS (Infrastructure monitoring)
    # ======================================================
    path(
        "servers/",
        InfraServersStatusAPIView.as_view(),
        name="infra-servers-status",
    ),

    # ======================================================
    # 5️⃣ SERVER DETAIL (Deep monitoring)
    # ======================================================
    path(
        "servers/<int:agent_id>/",
        InfraServerDetailAPIView.as_view(),
        name="infra-server-detail",
    ),

]