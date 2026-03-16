from django.urls import path
from api.views import EventCreateAPIView
from api.views.stats import DashboardStatsView
from signals.views import SignalListAPIView, SignalCreateAPIView


urlpatterns = [
    path("events/", EventCreateAPIView.as_view(), name="api-events"),

    # 📡 SIGNALS
    path("signals/", SignalListAPIView.as_view(), name="api-signals"),          # GET
    path("signals/create/", SignalCreateAPIView.as_view(), name="signal-create"),  # POST

    path("stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
]