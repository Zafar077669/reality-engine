from django.urls import path

from .views import (
    InfraHeartbeatAPIView,
    InfraMetricHistoryAPIView,
    AgentIncidentOverlayAPIView,
    InfraServersStatusAPIView,
    InfraServerDetailAPIView,
)


urlpatterns = [


    path(
        "heartbeat/",
        InfraHeartbeatAPIView.as_view(),
        name="infra-heartbeat",
    ),


    path(
        "metrics/<int:agent_id>/history/",
        InfraMetricHistoryAPIView.as_view(),
        name="infra-metrics-history",
    ),


    path(
        "metrics/<int:agent_id>/incidents/",
        AgentIncidentOverlayAPIView.as_view(),
        name="infra-metrics-incidents",
    ),


    path(
        "servers/",
        InfraServersStatusAPIView.as_view(),
        name="infra-servers-status",
    ),


 
    path(
        "servers/<int:agent_id>/",
        InfraServerDetailAPIView.as_view(),
        name="infra-server-detail",
    ),

]