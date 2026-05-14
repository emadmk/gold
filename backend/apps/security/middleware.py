"""
Defence-in-depth security middleware:

* Adds OWASP-recommended response headers (Traefik adds them too).
* Enforces Redis-backed token-bucket rate limits per route family.
"""
from __future__ import annotations

import time
from typing import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse

from apps.audit.emit import emit_event

from .ratelimit import allow


_DEFAULT_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=(self), payment=()",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
}


class SecurityHeadersMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        for k, v in _DEFAULT_HEADERS.items():
            response.setdefault(k, v)
        if settings.SERVICE_ENV == "prod":
            response.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains; preload",
            )
        return response


_RATE_RULES: list[tuple[str, str, int, int]] = [
    # (path-prefix, method, limit, window-seconds)
    ("/api/v1/auth/otp/request", "POST", 5, 15 * 60),
    ("/api/v1/auth/otp/verify", "POST", 5, 15 * 60),
    ("/api/v1/wallet/withdraw", "POST", 3, 60 * 60),
    ("/api/v1/orders", "POST", 60, 60),
]


class RateLimitMiddleware:
    """Token-bucket rate limit (Redis). Buckets keyed by (path-rule, user|ip)."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        rule = self._match(request)
        if rule:
            prefix, _method, limit, window = rule
            ident = self._ident(request)
            ok, remaining, reset = allow(
                key=f"rl:{prefix}:{ident}", limit=limit, window_s=window
            )
            if not ok:
                emit_event(
                    "security.ratelimit.breach",
                    severity="warning",
                    outcome="denied",
                    data={"path": prefix, "ident": ident, "limit": limit, "window_s": window},
                )
                resp = JsonResponse(
                    {"detail": "تعداد درخواست‌ها بیش از حد مجاز است. کمی بعد دوباره تلاش کنید."},
                    status=429,
                )
                resp["Retry-After"] = str(max(1, int(reset - time.time())))
                resp["X-RateLimit-Remaining"] = "0"
                return resp
            request.META["X-RateLimit-Remaining"] = str(remaining)
        return self.get_response(request)

    @staticmethod
    def _match(request: HttpRequest) -> tuple[str, str, int, int] | None:
        for prefix, method, limit, window in _RATE_RULES:
            if request.path.startswith(prefix) and request.method == method:
                return prefix, method, limit, window
        return None

    @staticmethod
    def _ident(request: HttpRequest) -> str:
        user = getattr(request, "user", None)
        if user and getattr(user, "is_authenticated", False):
            return f"u:{user.id}"
        return f"ip:{request.META.get('REMOTE_ADDR', '')}"
