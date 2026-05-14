"""
Base settings — shared by dev, prod, test.

Every secret is loaded via django-environ from .env / process env.
Never hard-code a credential here.
"""
from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import environ

# ---------------------------------------------------------------------------
# Paths & env
# ---------------------------------------------------------------------------
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
REPO_ROOT = BACKEND_DIR.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["*"]),
    CSRF_TRUSTED_ORIGINS=(list, []),
    CORS_ALLOWED_ORIGINS=(list, ["http://localhost:3000"]),
    TIME_ZONE=(str, "Asia/Tehran"),
    USE_TZ=(bool, True),
)
environ.Env.read_env(REPO_ROOT / ".env")

# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-secret-change-me")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

SERVICE_NAME = env("SERVICE_NAME", default="keyhan-backend")
SERVICE_VERSION = env("SERVICE_VERSION", default="0.1.0")
SERVICE_ENV = env("SERVICE_ENV", default="dev")

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "django_filters",
    "corsheaders",
    "channels",
    "django_celery_beat",
    "django_celery_results",
    "django_prometheus",
    "storages",
]

LOCAL_APPS = [
    "apps.audit",
    "apps.security",
    "apps.accounts",
    "apps.wallet",
    "apps.pricing",
    "apps.orders",
    "apps.payments",
    "apps.marketplace",
    "apps.coins",
    "apps.jewelry",
    "apps.delivery",
    "apps.notifications",
    "apps.admin_panel",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "apps.audit.middleware.RequestContextMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.security.middleware.SecurityHeadersMiddleware",
    "apps.security.middleware.RateLimitMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BACKEND_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DATABASES = {
    "default": env.db_url(
        "DATABASE_URL",
        default="postgres://keyhan:keyhan@postgres:5432/keyhan",
    ),
}
DATABASES["default"]["CONN_MAX_AGE"] = 60
DATABASES["default"]["OPTIONS"] = {"sslmode": env("DB_SSLMODE", default="prefer")}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Cache + Channels + Celery
# ---------------------------------------------------------------------------
REDIS_URL = env("REDIS_URL", default="redis://redis:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    },
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [REDIS_URL]},
    },
}

CELERY_BROKER_URL = env("CELERY_BROKER_URL", default=REDIS_URL)
CELERY_RESULT_BACKEND = "django-db"
CELERY_CACHE_BACKEND = "django-cache"
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=False)
CELERY_TIMEZONE = env("TIME_ZONE", default="Asia/Tehran")
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_TASK_TIME_LIMIT = 60 * 5
CELERY_TASK_SOFT_TIME_LIMIT = 60 * 4
CELERY_WORKER_HIJACK_ROOT_LOGGER = False
CELERY_WORKER_SEND_TASK_EVENTS = True
CELERY_TASK_SEND_SENT_EVENT = True

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 12}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# DRF
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "apps.accounts.auth.CookieJWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "apps.security.exceptions.exception_handler",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "EdDSA",
    "SIGNING_KEY": env("JWT_PRIVATE_KEY", default=""),
    "VERIFYING_KEY": env("JWT_PUBLIC_KEY", default=""),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_COOKIE": "keyhan_access",
    "AUTH_COOKIE_REFRESH": "keyhan_refresh",
    "AUTH_COOKIE_SECURE": True,
    "AUTH_COOKIE_HTTP_ONLY": True,
    "AUTH_COOKIE_SAMESITE": "Strict",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "KeyhanGold API",
    "DESCRIPTION": "Online gold & silver trading platform — Iranian market",
    "VERSION": SERVICE_VERSION,
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": "/api/v1/",
}

# ---------------------------------------------------------------------------
# CORS / CSRF
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=["http://localhost:3000"])
CORS_ALLOW_CREDENTIALS = True
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = "Strict"
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict"

# ---------------------------------------------------------------------------
# Static / media
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BACKEND_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BACKEND_DIR / "media"

# Object storage (MinIO / S3)
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": env("MINIO_BUCKET", default="keyhan-private"),
            "endpoint_url": env("MINIO_ENDPOINT", default="http://minio:9000"),
            "access_key": env("MINIO_ACCESS_KEY", default="keyhan"),
            "secret_key": env("MINIO_SECRET_KEY", default="keyhansecret"),
            "default_acl": "private",
            "querystring_auth": True,
            "querystring_expire": 300,
            "file_overwrite": False,
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# ---------------------------------------------------------------------------
# i18n
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "fa-ir"
TIME_ZONE = env("TIME_ZONE", default="Asia/Tehran")
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Security headers (defence-in-depth alongside Traefik)
# ---------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Override in prod.py
SECURE_HSTS_SECONDS = 0
SECURE_SSL_REDIRECT = False

# ---------------------------------------------------------------------------
# Observability
# ---------------------------------------------------------------------------
ELASTICSEARCH_HOSTS = env.list("ELASTICSEARCH_HOSTS", default=["http://elasticsearch:9200"])
ELASTICSEARCH_USER = env("ELASTICSEARCH_USER", default="elastic")
ELASTICSEARCH_PASSWORD = env("ELASTICSEARCH_PASSWORD", default="")
AUDIT_STREAM_PREFIX = "domain_events"
AUDIT_REDIS_MAXLEN = 1_000_000

SENTRY_DSN = env("SENTRY_DSN", default="")
OTEL_EXPORTER_OTLP_ENDPOINT = env("OTEL_EXPORTER_OTLP_ENDPOINT", default="")

# ---------------------------------------------------------------------------
# External providers
# ---------------------------------------------------------------------------
KAVENEGAR_API_KEY = env("KAVENEGAR_API_KEY", default="")
KAVENEGAR_OTP_TEMPLATE = env("KAVENEGAR_OTP_TEMPLATE", default="verify-login")

PAYMENT_GATEWAYS = {
    "zarinpal": {
        "merchant_id": env("ZARINPAL_MERCHANT_ID", default=""),
        "sandbox": env.bool("ZARINPAL_SANDBOX", default=True),
    },
    "idpay": {
        "api_key": env("IDPAY_API_KEY", default=""),
        "sandbox": env.bool("IDPAY_SANDBOX", default=True),
    },
    "payping": {
        "api_key": env("PAYPING_API_KEY", default=""),
        "sandbox": env.bool("PAYPING_SANDBOX", default=True),
    },
}

# ---------------------------------------------------------------------------
# Domain defaults (overridable from admin -> PricingFormula)
# ---------------------------------------------------------------------------
DOMAIN_DEFAULTS = {
    "buy_spread": "0.005",
    "sell_spread": "0.005",
    "commission_buy": "0.005",
    "commission_sell": "0.005",
    "silver_buy_spread": "0.01",
    "silver_sell_spread": "0.01",
    "silver_commission": "0.01",
    "min_commission_fixed_mg": "1",
    "withdraw_fee_rial": "20000",
    "delivery_processing_fee_pct": "0.03",
    "min_physical_delivery_mg": "5000",
    "delivery_lot_step_mg": "1000",
    "daily_yield_apr": "0.24",
    "aml_threshold_rial": "10000000000",  # 1B IRR
    "vat_pct": "0.09",
}

# ---------------------------------------------------------------------------
# Feature flags (Redis-backed; defaults here)
# ---------------------------------------------------------------------------
FEATURE_FLAGS_DEFAULT = {
    "marketplace": True,
    "silver_trading": True,
    "physical_delivery": True,
    "daily_yield": True,
    "two_factor_withdraw": True,
}

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@keyhan.gold")
