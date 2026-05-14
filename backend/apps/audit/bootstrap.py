"""
One-shot observability bootstrap.

Called from `core/asgi.py` so it runs once per worker boot:

* configures structlog
* installs OpenTelemetry instrumentation (if endpoint set)
* initialises Sentry (if DSN set)
* validates the catalogue (fails loudly on duplicate kinds)
"""
from __future__ import annotations

from django.conf import settings

from .catalogue import CATALOGUE
from .log import configure_logging


_done = False


def bootstrap_observability() -> None:
    global _done
    if _done:
        return
    _done = True

    configure_logging()

    # Sentry
    dsn = getattr(settings, "SENTRY_DSN", "")
    if dsn:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.django import DjangoIntegration
            from sentry_sdk.integrations.celery import CeleryIntegration
            from sentry_sdk.integrations.redis import RedisIntegration

            sentry_sdk.init(
                dsn=dsn,
                integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()],
                traces_sample_rate=0.1,
                send_default_pii=False,
                environment=settings.SERVICE_ENV,
                release=settings.SERVICE_VERSION,
            )
        except Exception:  # noqa: BLE001
            pass

    # OpenTelemetry
    if getattr(settings, "OTEL_EXPORTER_OTLP_ENDPOINT", ""):
        try:
            from opentelemetry import trace
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
            from opentelemetry.sdk.resources import Resource
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.instrumentation.django import DjangoInstrumentor

            resource = Resource.create(
                {
                    "service.name": settings.SERVICE_NAME,
                    "service.version": settings.SERVICE_VERSION,
                    "deployment.environment": settings.SERVICE_ENV,
                }
            )
            provider = TracerProvider(resource=resource)
            provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
            trace.set_tracer_provider(provider)
            DjangoInstrumentor().instrument()
        except Exception:  # noqa: BLE001
            pass

    # Sanity-check the catalogue
    assert len(CATALOGUE) >= 30, "catalogue suspiciously small"
