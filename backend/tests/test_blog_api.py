"""Blog API: list filters by published, detail bumps views."""
from __future__ import annotations

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.blog.models import Category, Post

pytestmark = pytest.mark.django_db


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(phone="09120000001")


@pytest.fixture
def category():
    return Category.objects.create(code="news", title_fa="اخبار", sort=10)


def _published(author, category, slug: str, **extra) -> Post:
    return Post.objects.create(
        author=author, category=category,
        title=f"عنوان {slug}", slug=slug,
        summary="خلاصه", body_md="متن.\n\nپاراگراف دوم.",
        state="published", published_at=timezone.now(),
        **extra,
    )


def test_list_excludes_drafts(author, category):
    _published(author, category, "p1")
    Post.objects.create(author=author, title="پیش‌نویس", slug="d1", body_md="x")
    res = APIClient().get("/api/v1/blog/posts").json()
    assert {p["slug"] for p in res["results"]} == {"p1"}


def test_detail_increments_views(author, category):
    p = _published(author, category, "viewme")
    assert p.views == 0
    APIClient().get(f"/api/v1/blog/posts/{p.slug}")
    p.refresh_from_db()
    assert p.views == 1


def test_draft_detail_404(author, category):
    Post.objects.create(author=author, title="نهان", slug="hidden", body_md="x")
    r = APIClient().get("/api/v1/blog/posts/hidden")
    assert r.status_code == 404
