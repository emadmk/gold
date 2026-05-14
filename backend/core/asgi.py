"""ASGI entry: HTTP + WebSocket (Channels)."""
from __future__ import annotations

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.prod")
django_app = get_asgi_application()

# Now that Django is configured, import everything that depends on it.
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.auth import AuthMiddlewareStack  # noqa: E402

from apps.audit.bootstrap import bootstrap_observability  # noqa: E402
from apps.pricing.routing import websocket_urlpatterns as pricing_ws  # noqa: E402
from apps.notifications.routing import websocket_urlpatterns as notif_ws  # noqa: E402

bootstrap_observability()

application = ProtocolTypeRouter(
    {
        "http": django_app,
        "websocket": AuthMiddlewareStack(URLRouter(pricing_ws + notif_ws)),
    }
)
