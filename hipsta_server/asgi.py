import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from apps.tickets.routing import websocket_urlpatterns

django_asgi_app = get_asgi_application()

import  apps.tickets.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hipsta_server.settings.development") 

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)