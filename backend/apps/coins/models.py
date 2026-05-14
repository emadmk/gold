"""Coin catalogue — reference data."""
from __future__ import annotations

from django.db import models


class CoinType(models.Model):
    code = models.SlugField(unique=True)  # emami, bahar, half, quarter, gerami
    title_fa = models.CharField(max_length=80)
    weight_mg = models.BigIntegerField()
    gold_content_mg = models.BigIntegerField(help_text="میلی‌گرم طلای خالص داخل سکه")
    image = models.ImageField(upload_to="coins/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.title_fa
