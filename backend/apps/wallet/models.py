"""Wallet aggregates: rial wallet, gold wallet, transaction ledger."""
from __future__ import annotations

import secrets
import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import CheckConstraint, Q
from django.utils.translation import gettext_lazy as _


def generate_gold_address() -> str:
    return "GLD-" + secrets.token_hex(16).upper()


class RialWallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rial_wallet"
    )
    tenant_id = models.CharField(max_length=40, default="default", db_index=True)
    currency = models.CharField(max_length=8, default="IRR")  # roadmap #10 seam
    balance_rial = models.BigIntegerField(default=0, validators=[MinValueValidator(0)])
    locked_rial = models.BigIntegerField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Rial wallet")
        constraints = [
            CheckConstraint(check=Q(balance_rial__gte=0), name="rialwallet_balance_nonneg"),
            CheckConstraint(check=Q(locked_rial__gte=0), name="rialwallet_locked_nonneg"),
            CheckConstraint(check=Q(locked_rial__lte=models.F("balance_rial")),
                            name="rialwallet_locked_le_balance"),
        ]

    @property
    def available_rial(self) -> int:
        return self.balance_rial - self.locked_rial


class GoldWallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="gold_wallet"
    )
    tenant_id = models.CharField(max_length=40, default="default", db_index=True)
    address = models.CharField(max_length=42, unique=True, default=generate_gold_address)
    balance_mg = models.BigIntegerField(default=0, validators=[MinValueValidator(0)])
    locked_mg = models.BigIntegerField(default=0, validators=[MinValueValidator(0)])
    silver_balance_mg = models.BigIntegerField(default=0, validators=[MinValueValidator(0)])
    silver_locked_mg = models.BigIntegerField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            CheckConstraint(check=Q(balance_mg__gte=0), name="goldwallet_gold_nonneg"),
            CheckConstraint(check=Q(silver_balance_mg__gte=0), name="goldwallet_silver_nonneg"),
            CheckConstraint(check=Q(locked_mg__lte=models.F("balance_mg")),
                            name="goldwallet_gold_locked_le_balance"),
            CheckConstraint(check=Q(silver_locked_mg__lte=models.F("silver_balance_mg")),
                            name="goldwallet_silver_locked_le_balance"),
        ]

    @property
    def available_gold_mg(self) -> int:
        return self.balance_mg - self.locked_mg

    @property
    def available_silver_mg(self) -> int:
        return self.silver_balance_mg - self.silver_locked_mg


class WalletTransaction(models.Model):
    TYPES = [
        ("deposit", _("واریز ریالی")),
        ("withdraw", _("برداشت ریالی")),
        ("buy_gold", _("خرید طلا")),
        ("sell_gold", _("فروش طلا")),
        ("buy_silver", _("خرید نقره")),
        ("sell_silver", _("فروش نقره")),
        ("transfer_in", _("انتقال ورودی")),
        ("transfer_out", _("انتقال خروجی")),
        ("yield_payout", _("سود روزانه")),
        ("delivery_burn", _("تحویل فیزیکی")),
        ("commission", _("کارمزد")),
        ("adjustment", _("اصلاح ادمین")),
        ("refund", _("بازگشت وجه")),
    ]
    ASSETS = [("rial", "rial"), ("gold", "gold"), ("silver", "silver")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="wallet_txs"
    )
    type = models.CharField(max_length=20, choices=TYPES)
    asset = models.CharField(max_length=8, choices=ASSETS)

    rial_amount = models.BigIntegerField(default=0)
    mg_amount = models.BigIntegerField(default=0)

    balance_after_rial = models.BigIntegerField(null=True, blank=True)
    balance_after_mg = models.BigIntegerField(null=True, blank=True)

    related_order = models.ForeignKey(
        "orders.Order", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="wallet_transactions",
    )
    event_id = models.CharField(max_length=32, blank=True, db_index=True)  # ULID of the audit event
    description = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["related_order"]),
            models.Index(fields=["type", "-created_at"]),
        ]
        verbose_name = _("Wallet transaction")
