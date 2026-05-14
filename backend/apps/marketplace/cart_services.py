"""
Cart business services.

API surface used by `apps/marketplace/views.py`:

* `get_or_create_cart(user)` → Cart
* `add_to_cart(cart, product, qty)` → CartItem
* `update_item(cart, item_id, qty)` → CartItem
* `remove_item(cart, item_id)` → None
* `refresh_locks(cart)` → list[dict]   # one entry per item: {item, locked, current, changed, expired}
* `apply_discount(cart, code)` → Cart
* `cart_totals(cart)` → dict with rial subtotal / shipping / discount / vat / final
"""
from __future__ import annotations

from typing import Iterable

from django.db import transaction
from django.utils import timezone

from apps.audit.emit import emit_event

from .cart import Cart, CartItem, DiscountCode
from .models import Product
from .services import compute_product_price


@transaction.atomic
def get_or_create_cart(user) -> Cart:
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


@transaction.atomic
def add_to_cart(cart: Cart, product: Product, qty: int = 1) -> CartItem:
    if qty < 1:
        raise ValueError("تعداد باید بزرگتر از صفر باشد.")
    if not product.is_active:
        raise ValueError("این محصول در دسترس نیست.")
    if qty > product.stock:
        raise ValueError(
            f"موجودی این محصول کافی نیست (موجود: {product.stock})."
        )
    unit = compute_product_price(product)
    item, created = CartItem.objects.select_for_update().get_or_create(
        cart=cart, product=product,
        defaults={"quantity": qty, "locked_unit_price_rial": unit,
                  "locked_at": timezone.now()},
    )
    if not created:
        item.quantity = min(item.quantity + qty, product.stock)
        item.locked_unit_price_rial = unit
        item.locked_at = timezone.now()
        item.save(update_fields=["quantity", "locked_unit_price_rial", "locked_at"])
    emit_event(
        "marketplace.cart.item_added",
        actor={"type": "user", "id": str(cart.user_id)},
        target={"type": "cart_item", "id": str(item.id), "owner_id": str(cart.user_id)},
        data={"product_id": str(product.id), "quantity": item.quantity,
              "locked_unit_price_rial": unit},
    )
    return item


@transaction.atomic
def update_item(cart: Cart, item_id, qty: int) -> CartItem | None:
    item = CartItem.objects.select_for_update().get(cart=cart, id=item_id)
    if qty < 1:
        prev_id = str(item.id)
        item.delete()
        emit_event(
            "marketplace.cart.item_removed",
            actor={"type": "user", "id": str(cart.user_id)},
            target={"type": "cart_item", "id": prev_id},
        )
        return None
    if qty > item.product.stock:
        raise ValueError(f"موجودی کافی نیست (موجود: {item.product.stock}).")
    item.quantity = qty
    item.save(update_fields=["quantity"])
    return item


def remove_item(cart: Cart, item_id) -> None:
    CartItem.objects.filter(cart=cart, id=item_id).delete()
    emit_event(
        "marketplace.cart.item_removed",
        actor={"type": "user", "id": str(cart.user_id)},
        target={"type": "cart_item", "id": str(item_id)},
    )


def refresh_locks(cart: Cart) -> list[dict]:
    """For each item, compute the live price + whether it differs from
    the lock. Returns a list of dicts the UI uses to render the price-
    change banner."""
    out: list[dict] = []
    for item in cart.items.select_related("product"):
        current = compute_product_price(item.product)
        out.append({
            "item_id": str(item.id),
            "product_id": str(item.product_id),
            "title": item.product.title,
            "locked": item.locked_unit_price_rial,
            "current": current,
            "delta": current - item.locked_unit_price_rial,
            "changed": current != item.locked_unit_price_rial,
            "expired": item.lock_expired,
            "locked_at": item.locked_at.isoformat(),
        })
    if any(r["changed"] for r in out):
        emit_event(
            "marketplace.cart.price_changed",
            actor={"type": "user", "id": str(cart.user_id)},
            target={"type": "cart", "id": str(cart.id), "owner_id": str(cart.user_id)},
            data={"items": out},
            severity="info",
        )
    return out


@transaction.atomic
def relock_cart(cart: Cart) -> None:
    """Refresh every item's locked price to the live price + reset timer.
    Called when the user clicks "update prices" or progresses past the
    cart step."""
    for item in cart.items.select_for_update().select_related("product"):
        item.locked_unit_price_rial = compute_product_price(item.product)
        item.locked_at = timezone.now()
        item.save(update_fields=["locked_unit_price_rial", "locked_at"])


def apply_discount(cart: Cart, code: str | None) -> Cart:
    if not code:
        cart.discount_code = None
        cart.save(update_fields=["discount_code"])
        return cart
    try:
        dc = DiscountCode.objects.get(code=code)
    except DiscountCode.DoesNotExist as exc:
        raise ValueError("کد تخفیف یافت نشد.") from exc
    if not dc.is_currently_valid():
        raise ValueError("کد تخفیف معتبر نیست.")
    cart.discount_code = dc
    cart.save(update_fields=["discount_code"])
    return cart


def cart_totals(cart: Cart) -> dict:
    subtotal = sum(
        i.locked_unit_price_rial * i.quantity for i in cart.items.all()
    )
    shipping = 0
    for i in cart.items.select_related("product"):
        shipping = max(shipping, int(i.product.shipping_cost_rial))
    discount = 0
    if cart.discount_code and cart.discount_code.is_currently_valid():
        discount = cart.discount_code.amount_off(subtotal)
    final = max(0, subtotal + shipping - discount)
    return {
        "subtotal_rial": subtotal,
        "shipping_rial": shipping,
        "discount_rial": discount,
        "final_rial": final,
        "items_count": cart.items.count(),
        "discount_code": cart.discount_code.code if cart.discount_code else None,
    }
