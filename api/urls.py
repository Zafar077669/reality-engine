from django.urls import path, include
from api.views import EventCreateAPIView
from api.views.stats import DashboardStatsView

urlpatterns = [
    path("events/", EventCreateAPIView.as_view(), name="api-events"),

    
    path("signals/", include("signals.urls")),

    path("stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
]