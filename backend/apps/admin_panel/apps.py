from django.apps import AppConfig


class AdminPanelConfig(AppConfig):
    name = "apps.admin_panel"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        # Apply admin-site branding side-effects
        from . import admin  # noqa: F401
