from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Relax cookie security for plain HTTP local dev
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SIMPLE_JWT["AUTH_COOKIE_SECURE"] = False  # type: ignore[name-defined]  # noqa: F405

INSTALLED_APPS += ["django_extensions"]  # type: ignore[name-defined]  # noqa: F405

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
