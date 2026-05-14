"""RBAC permissions (declared, then consumed by DRF + the state machine)."""
from __future__ import annotations

from rest_framework.permissions import BasePermission


class IsKYCVerified(BasePermission):
    message = "تکمیل احراز هویت برای این عملیات لازم است."

    def has_permission(self, request, view) -> bool:  # type: ignore[no-untyped-def]
        u = request.user
        return bool(u and u.is_authenticated and u.is_verified and not u.is_frozen)


class IsAdminRole(BasePermission):
    message = "دسترسی مدیریتی لازم است."

    def has_permission(self, request, view) -> bool:  # type: ignore[no-untyped-def]
        return bool(request.user and request.user.is_staff)


class IsVendor(BasePermission):
    message = "این صفحه مخصوص فروشندگان است."

    def has_permission(self, request, view) -> bool:  # type: ignore[no-untyped-def]
        u = request.user
        return bool(u and u.is_authenticated and u.is_vendor)
