"""Live price model + admin-tunable formula coefficients + quotes."""
from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


SOURCE_KEYS = [
    "gold_18k_750", "gold_18k_740", "gold_24k", "mesghal",
    "gold_melted_cash", "coin_emami", "coin_bahar", "coin_half",
    "coin_quarter", "coin_gerami", "silver_999", "silver_925",
    "ons_gold", "usd_free",
]


class PriceTick(models.Model):
    """One row per (source_key, captured_at) — full history."""

    source_key = models.CharField(max_length=40, db_index=True)
    rial_price = models.BigIntegerField()
    captured_at = models.DateTimeField(db_index=True)
    source = models.CharField(max_length=20, default="tgju")

    class Meta:
        indexes = [models.Index(fields=["source_key", "-captured_at"])]
        verbose_name = _("Price tick")

    def __str__(self) -> str:
        return f"{self.source_key}@{self.captured_at}: {self.rial_price}"


class PricingFormula(models.Model):
    """Coefficient registry — every coefficient is editable from the admin."""

    key = models.CharField(max_length=80, unique=True)
    # max_digits=24 gives 16 integer digits (≈ 10^16, more than enough for
    # any rial threshold including aml_threshold_rial = 10_000_000_000).
    value = models.DecimalField(max_digits=24, decimal_places=8)
    description = models.CharField(max_length=255, blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.key}={self.value}"


class PriceQuote(models.Model):
    """A frozen price (per mg) we showed a user — valid for ~30s."""

    quote_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="price_quotes",
    )
    asset = models.CharField(max_length=10)  # gold, silver
    side = models.CharField(max_length=4)    # buy, sell
    price_per_mg_rial = models.BigIntegerField()
    valid_until = models.DateTimeField()
    base_tick = models.ForeignKey(PriceTick, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["asset", "side", "-created_at"]),
            models.Index(fields=["valid_until"]),
        ]
        verbose_name = _("Price quote")
