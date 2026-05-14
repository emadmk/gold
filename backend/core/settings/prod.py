from .base import *  # noqa: F401,F403

DEBUG = False

SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True

# Sentry init lives in core/asgi.py via apps.audit.bootstrap
