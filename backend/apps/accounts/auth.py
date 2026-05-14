"""JWT authentication that reads from HttpOnly cookies."""
from __future__ import annotations

from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """Reads JWT from `keyhan_access` HttpOnly cookie; falls back to header."""

    def authenticate(self, request):  # type: ignore[no-untyped-def]
        cookie_name = settings.SIMPLE_JWT.get("AUTH_COOKIE", "keyhan_access")
        token = request.COOKIES.get(cookie_name)
        if token:
            validated = self.get_validated_token(token)
            return self.get_user(validated), validated
        return super().authenticate(request)
