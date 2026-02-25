from django.urls import path
from api.views import (
    EventCreateAPIView,
    SignalListAPIView,
    health_check,
)

urlpatterns = [
    path("events/", EventCreateAPIView.as_view(), name="api-events"),
    path("signals/", SignalListAPIView.as_view(), name="api-signals"),
    path("health/", health_check),
]