"""Jewellery taxonomy — categories + tags. Products live in `marketplace`."""
from __future__ import annotations

from django.db import models


class JewelryCategory(models.Model):
    code = models.SlugField(unique=True)
    title_fa = models.CharField(max_length=80)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True,
                               related_name="children")
    icon = models.CharField(max_length=80, blank=True)
    sort = models.PositiveSmallIntegerField(default=100)

    class Meta:
        ordering = ["sort", "title_fa"]

    def __str__(self) -> str:
        return self.title_fa
