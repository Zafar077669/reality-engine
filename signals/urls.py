# signals/urls.py
from django.urls import path
from .views import SignalListAPIView, SignalCreateAPIView

urlpatterns = [
    path("", SignalListAPIView.as_view(), name="signal-list"),          # GET
    path("create/", SignalCreateAPIView.as_view(), name="signal-create"),  # POST
]