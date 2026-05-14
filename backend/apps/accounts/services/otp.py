"""OTP service: generate, send (Kavenegar), verify."""
from __future__ import annotations

import secrets
from datetime import timedelta

import httpx
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from django.conf import settings
from django.utils import timezone

from apps.audit.emit import emit_event
from apps.security.crypto import hash_sha256

from ..models import OTPCode, User


OTP_VALIDITY_SECONDS = 120
OTP_MAX_ATTEMPTS = 5
_hasher = PasswordHasher(time_cost=3, memory_cost=64 * 1024, parallelism=2)


def _generate_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def request_otp(phone: str, purpose: str = "login") -> str:
    code = _generate_code()
    OTPCode.objects.create(
        phone=phone,
        code_hash=_hasher.hash(code),
        purpose=purpose,
        expires_at=timezone.now() + timedelta(seconds=OTP_VALIDITY_SECONDS),
    )
    _send_via_kavenegar(phone, code)
    emit_event(
        "accounts.otp.requested",
        target={"type": "phone", "id": hash_sha256(phone)[:16]},
        data={"purpose": purpose},
    )
    return code if settings.SERVICE_ENV != "prod" else ""


def verify_otp(phone: str, code: str, purpose: str = "login") -> bool:
    qs = (
        OTPCode.objects.filter(
            phone=phone, purpose=purpose, used=False, expires_at__gt=timezone.now()
        )
        .order_by("-created_at")
    )
    otp = qs.first()
    if not otp:
        emit_event("accounts.otp.rejected", outcome="failure", data={"reason": "not_found"})
        return False
    if otp.attempts >= OTP_MAX_ATTEMPTS:
        emit_event("accounts.otp.rejected", outcome="failure", data={"reason": "too_many_attempts"})
        emit_event("security.login.brute_force", severity="warning",
                   target={"type": "phone", "id": hash_sha256(phone)[:16]})
        return False
    try:
        _hasher.verify(otp.code_hash, code)
    except VerifyMismatchError:
        otp.attempts += 1
        otp.save(update_fields=["attempts"])
        emit_event("accounts.otp.rejected", outcome="failure", data={"reason": "mismatch"})
        return False
    otp.used = True
    otp.save(update_fields=["used"])
    emit_event("accounts.otp.verified", target={"type": "phone", "id": hash_sha256(phone)[:16]})
    return True


def upsert_user(phone: str) -> tuple[User, bool]:
    user, created = User.objects.get_or_create(phone=phone, defaults={"is_phone_verified": True})
    if not user.is_phone_verified:
        user.is_phone_verified = True
        user.save(update_fields=["is_phone_verified"])
    if created:
        emit_event(
            "accounts.user.registered",
            actor={"type": "user", "id": str(user.id)},
            target={"type": "user", "id": str(user.id)},
        )
    return user, created


def _send_via_kavenegar(phone: str, code: str) -> None:
    api_key = settings.KAVENEGAR_API_KEY
    template = settings.KAVENEGAR_OTP_TEMPLATE
    if not api_key:
        return  # dev mode — code printed in response or in logs
    url = f"https://api.kavenegar.com/v1/{api_key}/verify/lookup.json"
    try:
        with httpx.Client(timeout=8) as c:
            r = c.get(url, params={"receptor": phone, "token": code, "template": template})
        if r.status_code < 300:
            emit_event("accounts.otp.delivered",
                       target={"type": "phone", "id": hash_sha256(phone)[:16]},
                       data={"status": r.status_code})
    except Exception as exc:  # noqa: BLE001
        emit_event("accounts.otp.delivered", outcome="failure",
                   severity="warning", data={"error": repr(exc)})
