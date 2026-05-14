"""Health & metrics views."""
from __future__ import annotations

from django.conf import settings
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.views import View
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST


class HealthView(View):
    """Liveness + dependency health probe."""

    def get(self, request) -> JsonResponse:  # type: ignore[no-untyped-def]
        status: dict[str, object] = {"service": settings.SERVICE_NAME, "ok": True, "deps": {}}
        # DB
        try:
            with connection.cursor() as c:
                c.execute("SELECT 1")
            status["deps"]["db"] = "ok"
        except Exception as exc:  # noqa: BLE001
            status["deps"]["db"] = f"err: {exc!r}"
            status["ok"] = False
        # Redis
        try:
            import redis

            r = redis.Redis.from_url(settings.REDIS_URL)
            r.ping()
            status["deps"]["redis"] = "ok"
        except Exception as exc:  # noqa: BLE001
            status["deps"]["redis"] = f"err: {exc!r}"
            status["ok"] = False
        return JsonResponse(status, status=200 if status["ok"] else 503)


class MetricsView(View):
    """Prometheus exposition (django-prometheus also installs its own)."""

    def get(self, request) -> HttpResponse:  # type: ignore[no-untyped-def]
        return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)
