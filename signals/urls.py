from django.urls import path
from .views import SignalListAPIView, SignalCreateAPIView, MetricsView

urlpatterns = [
    path("", SignalListAPIView.as_view(), name="signal-list"),          
    path("create/", SignalCreateAPIView.as_view(), name="signal-create"),  

    
    path("metrics/", MetricsView.as_view(), name="signal-metrics"),
]