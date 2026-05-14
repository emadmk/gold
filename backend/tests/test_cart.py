"""Cart operations: add, update, remove, price lock + expiry."""
from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.marketplace.cart import PRICE_LOCK_SECONDS
from apps.marketplace.cart_services import (
    add_to_cart,
    apply_discount,
    cart_totals,
    get_or_create_cart,
    refresh_locks,
    relock_cart,
    remove_item,
)
from apps.marketplace.models import DiscountCode, Product, Vendor
from apps.pricing.models import PriceTick

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _seed_tick(db):
    PriceTick.objects.create(
        source_key="gold_18k_750", rial_price=20_000_000_000,  # 20M toman / g (rial)
        captured_at=timezone.now(),
    )


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create(phone="09125550001",
                                            is_verified=True)


@pytest.fixture
def vendor(user, django_user_model):
    vu = django_user_model.objects.create(phone="09125550002", is_vendor=True)
    return Vendor.objects.create(
        user=vu, shop_name="ش", shop_slug="s", legal_name="ل", state="approved",
    )


@pytest.fixture
def product(vendor):
    return Product.objects.create(
        vendor=vendor, category="jewelry", title="انگشتر",
        slug="ring-1", sku="R1",
        weight_mg=5000, karat=750,
        manufacturing_fee_pct=Decimal("0.14"),
        vendor_margin_pct=Decimal("0.07"),
        stock=5,
    )


def test_add_to_cart_locks_price(user, product):
    cart = get_or_create_cart(user)
    item = add_to_cart(cart, product, qty=1)
    assert item.quantity == 1
    assert item.locked_unit_price_rial > 0


def test_add_more_than_stock_blocked(user, product):
    cart = get_or_create_cart(user)
    with pytest.raises(ValueError):
        add_to_cart(cart, product, qty=99)


def test_remove_item(user, product):
    cart = get_or_create_cart(user)
    item = add_to_cart(cart, product, qty=1)
    remove_item(cart, item.id)
    assert cart.items.count() == 0


def test_refresh_locks_detects_price_change(user, product):
    cart = get_or_create_cart(user)
    add_to_cart(cart, product, qty=1)
    # Bump the underlying tick price
    PriceTick.objects.create(
        source_key="gold_18k_750", rial_price=30_000_000_000,
        captured_at=timezone.now(),
    )
    state = refresh_locks(cart)
    assert state[0]["changed"] is True
    assert state[0]["current"] > state[0]["locked"]


def test_lock_expires_after_6_minutes(user, product):
    cart = get_or_create_cart(user)
    item = add_to_cart(cart, product, qty=1)
    item.locked_at = timezone.now() - timedelta(seconds=PRICE_LOCK_SECONDS + 1)
    item.save()
    state = refresh_locks(cart)
    assert state[0]["expired"] is True


def test_relock_resets_timer(user, product):
    cart = get_or_create_cart(user)
    item = add_to_cart(cart, product, qty=1)
    item.locked_at = timezone.now() - timedelta(minutes=10)
    item.save()
    relock_cart(cart)
    state = refresh_locks(cart)
    assert state[0]["expired"] is False


def test_apply_percentage_discount(user, product):
    cart = get_or_create_cart(user)
    add_to_cart(cart, product, qty=2)
    DiscountCode.objects.create(
        code="OFF10", kind="percent", value=Decimal("0.10"),
        is_active=True, min_order_rial=0,
    )
    apply_discount(cart, "OFF10")
    t = cart_totals(cart)
    assert t["discount_rial"] > 0
    assert t["final_rial"] == t["subtotal_rial"] + t["shipping_rial"] - t["discount_rial"]


def test_apply_flat_discount(user, product):
    cart = get_or_create_cart(user)
    add_to_cart(cart, product, qty=1)
    DiscountCode.objects.create(
        code="FLAT", kind="flat", value=Decimal("1000000"),
        is_active=True,
    )
    apply_discount(cart, "FLAT")
    t = cart_totals(cart)
    assert t["discount_rial"] == 1_000_000


def test_min_order_blocks_small_subtotal(user, product):
    cart = get_or_create_cart(user)
    add_to_cart(cart, product, qty=1)
    DiscountCode.objects.create(
        code="VIP", kind="percent", value=Decimal("0.20"),
        min_order_rial=10**15, is_active=True,
    )
    apply_discount(cart, "VIP")
    t = cart_totals(cart)
    # subtotal way below 10^15, so no discount applied
    assert t["discount_rial"] == 0


def test_invalid_code(user, product):
    cart = get_or_create_cart(user)
    add_to_cart(cart, product, qty=1)
    with pytest.raises(ValueError):
        apply_discount(cart, "NOPE")


def test_expired_code_rejected(user, product):
    cart = get_or_create_cart(user)
    add_to_cart(cart, product, qty=1)
    DiscountCode.objects.create(
        code="OLD", kind="percent", value=Decimal("0.5"),
        is_active=True, valid_until=timezone.now() - timedelta(days=1),
    )
    with pytest.raises(ValueError):
        apply_discount(cart, "OLD")
