from django.urls import path

from incidents.views import (
    IncidentListAPIView,
    IncidentAssignAPIView,
    IncidentResolveAPIView,
    IncidentAcknowledgeAPIView,
)

app_name = "incidents"

urlpatterns = [
    path("", IncidentListAPIView.as_view(), name="incident-list"),
    path("<int:pk>/assign/", IncidentAssignAPIView.as_view(), name="incident-assign"),
    path("<int:pk>/resolve/", IncidentResolveAPIView.as_view(), name="incident-resolve"),
    path("<int:pk>/ack/", IncidentAcknowledgeAPIView.as_view(), name="incident-ack"),
]