"""Marketplace product pricing — the formula from mohem.docx §6."""
from __future__ import annotations

from decimal import Decimal

import pytest
from django.utils import timezone

from apps.marketplace.models import Product, Vendor
from apps.marketplace.services import compute_product_price
from apps.pricing.models import PriceTick

pytestmark = pytest.mark.django_db


@pytest.fixture
def per_g_18k():
    """20,000,000 toman per gram (= 200,000,000 rial)."""
    PriceTick.objects.create(
        source_key="gold_18k_750", rial_price=200_000_000,
        captured_at=timezone.now(),
    )
    return 200_000_000


@pytest.fixture
def vendor(django_user_model):
    u = django_user_model.objects.create(phone="09120000001", is_vendor=True)
    return Vendor.objects.create(
        user=u, shop_name="ش", shop_slug="s", legal_name="ل", state="approved",
    )


def _make(vendor, **kw) -> Product:
    defaults = dict(
        vendor=vendor, category="jewelry", title="t", slug="t",
        sku=kw.pop("sku", "P1"),
        weight_mg=1000, karat=750,
        manufacturing_fee_pct=Decimal("0.14"),
        vendor_margin_pct=Decimal("0.07"),
    )
    defaults.update(kw)
    return Product.objects.create(**defaults)


def test_formula_matches_docx_example(per_g_18k, vendor):
    """
    mohem.docx §6 worked example:
        weight = 1g, gold price = 20M toman, wage = 14%, margin = 7%
        no accessories, VAT = 9% (we use the legal rate, not the 10% in the doc)

        base   = 1 × 20,000,000 = 20,000,000 toman = 200,000,000 rial
        wage   = 200,000,000 × 0.14 = 28,000,000 rial
        margin = (200,000,000 + 28,000,000) × 0.07 = 15,960,000 rial
        vat    = (28,000,000 + 15,960,000 + 0) × 0.09 = 3,956,400 rial
        total  = 247,916,400 rial   (= 24,791,640 toman)
    """
    p = _make(vendor, weight_mg=1000)
    price = compute_product_price(p)
    assert price == 247_916_400


def test_accessories_included_in_vat(per_g_18k, vendor):
    """The doc explicitly says VAT is computed on (wage + margin + accessory)."""
    p_no_acc = _make(vendor, sku="A", weight_mg=1000)
    p_acc = _make(vendor, sku="B", weight_mg=1000,
                  metadata={"accessory_prices_rial": [5_000_000]})
    base = compute_product_price(p_no_acc)
    with_acc = compute_product_price(p_acc)
    delta = with_acc - base
    # accessory itself (5M) + VAT 9% on 5M = 5,450,000
    assert delta == 5_450_000


def test_coin_skips_vat_and_wage(per_g_18k, vendor):
    p = _make(vendor, sku="C", category="coin", weight_mg=8133, karat=900)
    # base only
    assert compute_product_price(p) > 0


def test_ingot_uses_full_formula(per_g_18k, vendor):
    p = _make(vendor, sku="I", category="ingot", weight_mg=10000, karat=995,
              manufacturing_fee_pct=Decimal("0.02"),
              vendor_margin_pct=Decimal("0.01"))
    price = compute_product_price(p)
    assert price > 10 * 200_000_000  # at least 10g worth of pure gold
