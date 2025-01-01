# asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from apps.tickets.routing import websocket_urlpatterns as ticket_urlpatterns
from apps.notifications.routing import websocket_urlpatterns as notification_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hipsta_server.settings.development")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                ticket_urlpatterns + notification_urlpatterns
            )
        )
    ),
})
