from django.apps import AppConfig


class AuditConfig(AppConfig):
    name = "apps.audit"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        # Register catalogue at import time so emit_event can validate kinds
        from . import catalogue  # noqa: F401
        from . import signals  # noqa: F401
