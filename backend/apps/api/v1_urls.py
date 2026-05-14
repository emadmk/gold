"""API v1 — single entry point that pulls each app's urls."""
from __future__ import annotations

from django.urls import include, path

urlpatterns = [
    path("", include("apps.accounts.urls")),
    path("", include("apps.wallet.urls")),
    path("", include("apps.pricing.urls")),
    path("", include("apps.orders.urls")),
    path("", include("apps.payments.urls")),
    path("", include("apps.marketplace.urls")),
    path("", include("apps.delivery.urls")),
    path("", include("apps.notifications.urls")),
    path("", include("apps.admin_panel.urls")),
]
