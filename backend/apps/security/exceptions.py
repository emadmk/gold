"""DRF exception handler: Persian messages + audit event on auth/perm denial."""
from __future__ import annotations

from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_default

from apps.audit.emit import emit_event


def exception_handler(exc, context):  # type: ignore[no-untyped-def]
    response = drf_default(exc, context)
    if isinstance(exc, exceptions.PermissionDenied):
        emit_event(
            "security.permission.denied",
            severity="warning",
            outcome="denied",
            data={"view": context.get("view").__class__.__name__ if context.get("view") else ""},
        )
    if response is not None:
        # Normalise to Persian-friendly "detail"
        if "detail" not in response.data and isinstance(response.data, dict):
            response.data = {"detail": "خطایی رخ داد", "errors": response.data}
        elif isinstance(response.data, list):
            response.data = {"detail": "خطایی رخ داد", "errors": response.data}
    return response
