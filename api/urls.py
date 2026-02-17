from django.urls import path
from .views import EventCreateAPIView, SignalListAPIView

urlpatterns = [
    path("events/", EventCreateAPIView.as_view(), name="api-events"),
    path("signals/", SignalListAPIView.as_view(), name="api-signals"),
]
