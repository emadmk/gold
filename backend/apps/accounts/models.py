"""
Accounts: User + OTP + KYC.

Multi-tenant ready: `tenant_id` lives here so every downstream aggregate
can carry its own copy. Roadmap #14 (white-label) needs no migration.
"""
from __future__ import annotations

import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.security.fields import EncryptedCharField


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, phone: str, password: str | None = None, **extra: object):
        if not phone:
            raise ValueError("phone is required")
        user = self.model(phone=phone, **extra)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone: str, password: str, **extra: object):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("is_verified", True)
        extra.setdefault("is_phone_verified", True)
        return self.create_user(phone, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    TIERS = [("standard", "Standard"), ("plus", "Plus"), ("pro", "Pro")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.CharField(max_length=40, default="default", db_index=True)

    phone = models.CharField(max_length=11, unique=True, db_index=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    first_name = models.CharField(max_length=80, blank=True)
    last_name = models.CharField(max_length=80, blank=True)

    # PII (encrypted at rest via Fernet)
    national_id = EncryptedCharField(max_length=255, blank=True)
    national_id_hash = models.CharField(max_length=64, blank=True, db_index=True)
    father_name = models.CharField(max_length=80, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    iban = EncryptedCharField(max_length=255, blank=True)
    iban_hash = models.CharField(max_length=64, blank=True, db_index=True)

    # Flags
    is_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default=False)
    is_frozen = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Roadmap seams (#5, #17, #20) — present from v1 on purpose
    tier = models.CharField(max_length=10, choices=TIERS, default="standard")
    referred_by = models.ForeignKey(
        "self", null=True, blank=True, related_name="referrals", on_delete=models.SET_NULL
    )
    share_trades = models.BooleanField(default=False)

    # 2FA
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = EncryptedCharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        indexes = [
            models.Index(fields=["tenant_id", "phone"]),
            models.Index(fields=["is_verified", "is_phone_verified"]),
        ]

    def __str__(self) -> str:
        return self.phone

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.phone


class OTPCode(models.Model):
    PURPOSES = [
        ("login", _("ورود/ثبت‌نام")),
        ("withdraw", _("تأیید برداشت")),
        ("transfer", _("تأیید انتقال")),
        ("change_iban", _("تغییر شبا")),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=11, db_index=True)
    code_hash = models.CharField(max_length=128)  # argon2 hash of the 6-digit code
    purpose = models.CharField(max_length=20, choices=PURPOSES)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["phone", "purpose", "expires_at"])]


class KYCSubmission(models.Model):
    STATUSES = [
        ("empty", _("هیچ مدرکی ارسال نشده")),
        ("submitted", _("ارسال شد")),
        ("under_review", _("در حال بررسی")),
        ("approved", _("تأیید شد")),
        ("rejected", _("رد شد")),
        ("requires_more", _("نیاز به اطلاعات بیشتر")),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="kyc_submissions")
    state = models.CharField(max_length=20, choices=STATUSES, default="empty")

    national_card_front = models.FileField(upload_to="kyc/", blank=True, null=True)
    national_card_back = models.FileField(upload_to="kyc/", blank=True, null=True)
    selfie_with_card = models.FileField(upload_to="kyc/", blank=True, null=True)
    birth_certificate = models.FileField(upload_to="kyc/", blank=True, null=True)
    video_attestation = models.FileField(upload_to="kyc/", blank=True, null=True)
    card_pan_masked = models.CharField(max_length=20, blank=True)

    rejection_reason = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="kyc_reviews"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("KYC Submission")
        verbose_name_plural = _("KYC Submissions")
