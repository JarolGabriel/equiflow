import os

import django
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")


django.setup()


django_asgi_app = get_asgi_application()


from channels.routing import ProtocolTypeRouter, URLRouter

from apps.alerts.middleware import JWTAuthMiddleware
from apps.alerts.routing import websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": JWTAuthMiddleware(URLRouter(websocket_urlpatterns)),
    }
)
