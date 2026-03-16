"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""


import os

from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from signals.routing import websocket_urlpatterns


# ==========================================================
# Django settings
# ==========================================================

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


# ==========================================================
# Django ASGI application
# ==========================================================

django_asgi_app = get_asgi_application()


# ==========================================================
# Main ASGI Router
# ==========================================================

application = ProtocolTypeRouter({

    # Standard HTTP requests
    "http": django_asgi_app,

    # WebSocket connections
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),

})