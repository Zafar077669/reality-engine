from django.urls import re_path

from .consumers import (
    SignalConsumer,
    MetricsConsumer,
)



websocket_urlpatterns = [

    # Realtime signals stream
    re_path(
        r"ws/signals/$",
        SignalConsumer.as_asgi(),
    ),

    # Realtime metrics stream
    re_path(
        r"ws/metrics/$",
        MetricsConsumer.as_asgi(),
    ),

]