"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from apps.alerts.middleware import JWTAuthMiddleware
from apps.alerts.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        # Standard HTTP requests
        "http": django_asgi_app,
        # WebSocket requests
        "websocket": JWTAuthMiddleware(URLRouter(websocket_urlpatterns)),
    }
)
