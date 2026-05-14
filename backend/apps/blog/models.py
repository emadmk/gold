"""Blog: Tag, Category, Post."""
from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    code = models.SlugField(unique=True)
    title_fa = models.CharField(max_length=120)
    sort = models.PositiveSmallIntegerField(default=100)

    class Meta:
        ordering = ["sort", "title_fa"]
        verbose_name = _("Category")

    def __str__(self) -> str:
        return self.title_fa


class Tag(models.Model):
    code = models.SlugField(unique=True)
    title_fa = models.CharField(max_length=80)

    def __str__(self) -> str:
        return self.title_fa


class Post(models.Model):
    STATES = [
        ("draft", _("پیش‌نویس")),
        ("published", _("منتشر شد")),
        ("archived", _("بایگانی")),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.CharField(max_length=40, default="default", db_index=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="posts"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    summary = models.CharField(max_length=300, blank=True)
    body_md = models.TextField()
    cover_image = models.ImageField(upload_to="blog/covers/", null=True, blank=True)
    state = models.CharField(max_length=10, choices=STATES, default="draft")
    metadata = models.JSONField(default=dict, blank=True)
    views = models.PositiveIntegerField(default=0)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["state", "-published_at"]),
            models.Index(fields=["category", "-published_at"]),
        ]

    def __str__(self) -> str:
        return self.title
