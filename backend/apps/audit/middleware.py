"""
Request-context middleware.

Pulls (or generates) a request_id, trace_id, user_id and IP for every HTTP
request and binds them into a contextvar that the logger and emit_event read.
"""
from __future__ import annotations

from typing import Callable

from django.http import HttpRequest, HttpResponse
from ulid import ULID

from .context import RequestContext, set_context, clear_context


class RequestContextMiddleware:
    """Bind correlation IDs for the lifetime of the request."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request_id = request.headers.get("X-Request-Id") or str(ULID())
        trace_id = request.headers.get("Traceparent", "").split("-")[1] if "Traceparent" in request.headers else ""
        ip = self._client_ip(request)
        user_id = ""
        roles: tuple[str, ...] = ()
        # auth user not yet resolved here; refreshed after auth middleware runs.

        token = set_context(
            RequestContext(
                request_id=request_id,
                trace_id=trace_id,
                user_id=user_id,
                ip=ip,
                user_agent=request.headers.get("User-Agent", "")[:255],
                roles=roles,
            )
        )
        request.request_id = request_id  # type: ignore[attr-defined]
        try:
            response = self.get_response(request)
        finally:
            clear_context()
            # we don't reset() with the token because Django middleware doesn't span tasks
            del token  # silence linter

        response["X-Request-Id"] = request_id
        return response

    @staticmethod
    def _client_ip(request: HttpRequest) -> str:
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")
