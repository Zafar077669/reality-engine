import json
from channels.generic.websocket import AsyncWebsocketConsumer


# ==========================================================
# 🔴 REALTIME SIGNAL STREAM
# ==========================================================

class SignalConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for realtime signals stream.

    Frontend subscribes to this socket to receive
    newly generated signals instantly.
    """

    group_name = "signals_stream"

    async def connect(self):
        """
        Client WebSocket connection.
        Adds client to signals stream group.
        """

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """
        Client disconnected.
        Remove from group.
        """

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def signal_update(self, event):
        """
        Receive signal event from backend
        and forward to frontend client.
        """

        data = event.get("data", {})

        await self.send(
            text_data=json.dumps(data)
        )


# ==========================================================
# 📈 REALTIME METRICS STREAM
# ==========================================================

class MetricsConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for realtime infrastructure metrics.

    Used for live CPU / RAM / DISK monitoring charts.
    """

    group_name = "metrics_stream"

    async def connect(self):
        """
        Client connects to metrics stream.
        """

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """
        Remove client from metrics group.
        """

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_metric(self, event):
        """
        Send realtime metric update to frontend.
        """

        data = event.get("data", {})

        await self.send(
            text_data=json.dumps(data)
        )