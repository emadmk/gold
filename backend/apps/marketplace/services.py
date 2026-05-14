"""
Marketplace business services.

* `compute_product_price`  — given a Product and live gold/silver tick,
  compute the rial price using SECURITY-§Domain VAT rules (9% on
  manufacturing fee + vendor margin only).
* `apply_to_vendor` — vendor onboarding.
* `checkout` — turn a cart of (product, qty) tuples into an Order with
  rial-locked funds and a 30-min payment deadline.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Iterable, Sequence

from django.db import transaction
from django.utils import timezone

from apps.accounts.permissions import IsKYCVerified  # noqa: F401  (re-export marker)
from apps.audit.emit import emit_event
from apps.audit.state_machine import vendor_sm
from apps.orders.models import Order, OrderItem
from apps.orders.services import PAYMENT_DEADLINE_MIN
from apps.pricing.models import PriceTick
from apps.wallet import services as wallet_svc

from .models import Product, Vendor

VAT_PCT = Decimal("0.09")


def _latest_18k_per_g() -> int:
    t = PriceTick.objects.filter(source_key="gold_18k_750").order_by("-captured_at").first()
    return int(t.rial_price) if t else 0


def _latest_999_per_g() -> int:
    t = PriceTick.objects.filter(source_key="silver_999").order_by("-captured_at").first()
    return int(t.rial_price) if t else 0


def compute_product_price(p: Product) -> int:
    """Return the rial unit price for this product right now.

    Implements the formula from `mohem.docx §6`:

        base    = weight × per_g          (in rial)
        wage    = base × wage_pct
        margin  = (base + wage) × margin_pct   ← compounded
        accessory = sum(p.metadata["accessory_prices_rial"])
        vat     = (wage + margin + accessory) × vat_pct   (jewelry only)
        final   = base + wage + margin + accessory + vat + fixed_extra_rial

    Silver and coin shortcuts skip the wage/margin/VAT layer.
    """
    if p.category == "silver":
        per_g = _latest_999_per_g()
        base = int(Decimal(p.weight_mg) * Decimal(per_g) / Decimal(1000))
        return base + int(p.fixed_extra_rial)
    if p.category == "coin":
        per_g = _latest_18k_per_g()
        equiv_18k_mg = int(Decimal(p.weight_mg) * Decimal(p.karat) / Decimal(750))
        base = int(Decimal(equiv_18k_mg) * Decimal(per_g) / Decimal(1000))
        return base + int(p.fixed_extra_rial)
    # melted / jewelry / leather_bracelet / ingot — full formula
    per_g = _latest_18k_per_g()
    equiv_18k_mg = int(Decimal(p.weight_mg) * Decimal(p.karat) / Decimal(750))
    base = int(Decimal(equiv_18k_mg) * Decimal(per_g) / Decimal(1000))
    wage = int(Decimal(base) * Decimal(p.manufacturing_fee_pct))
    margin = int(Decimal(base + wage) * Decimal(p.vendor_margin_pct))
    accessories = int(sum(
        Decimal(str(x)) for x in (p.metadata or {}).get("accessory_prices_rial", []) if x
    ))
    vat = (
        int((Decimal(wage) + Decimal(margin) + Decimal(accessories)) * VAT_PCT)
        if p.category == "jewelry" else 0
    )
    return base + wage + margin + accessories + vat + int(p.fixed_extra_rial)


def apply_to_vendor(*, user, shop_name: str, shop_slug: str, legal_name: str,
                    iban: str, city: str = "", description: str = "") -> Vendor:
    v, created = Vendor.objects.get_or_create(
        user=user,
        defaults={
            "shop_name": shop_name, "shop_slug": shop_slug,
            "legal_name": legal_name, "iban": iban,
            "city": city, "description": description, "state": "applied",
        },
    )
    if created:
        user.is_vendor = True
        user.save(update_fields=["is_vendor"])
        emit_event(
            "marketplace.vendor.applied",
            actor={"type": "user", "id": str(user.id)},
            target={"type": "vendor", "id": str(v.id), "owner_id": str(user.id)},
            data={"shop_name": shop_name, "shop_slug": shop_slug},
        )
    return v


def approve_vendor(v: Vendor, *, admin) -> Vendor:
    vendor_sm.fire(
        v, trigger="vendor.approve",
        actor={"type": "admin", "id": str(admin.id)},
        target={"type": "vendor", "id": str(v.id), "owner_id": str(v.user_id)},
    )
    return v


def suspend_vendor(v: Vendor, *, admin, reason: str = "") -> Vendor:
    vendor_sm.fire(
        v, trigger="vendor.suspend",
        actor={"type": "admin", "id": str(admin.id)},
        target={"type": "vendor", "id": str(v.id), "owner_id": str(v.user_id)},
        data={"reason": reason},
    )
    return v


@transaction.atomic
def checkout(*, user, items: Sequence[tuple[Product, int]],
             shipping_address: str, recipient_name: str,
             recipient_phone: str) -> Order:
    """Create a marketplace Order from a list of (product, qty) tuples."""
    if not items:
        raise ValueError("سبد خرید خالی است.")
    vendors = {p.vendor_id for p, _ in items}
    if len(vendors) > 1:
        raise ValueError("سفارش‌های چند فروشنده پشتیبانی نمی‌شود؛ هر فروشنده جداگانه.")

    total = 0
    line_data: list[dict] = []
    for p, qty in items:
        if qty < 1 or qty > p.stock:
            raise ValueError(f"موجودی {p.title} کافی نیست.")
        unit = compute_product_price(p)
        line_total = unit * qty
        total += line_total
        line_data.append({
            "product": p, "qty": qty, "unit": unit, "line_total": line_total,
            "title": p.title,
            "metadata": {
                "weight_mg": p.weight_mg, "karat": p.karat,
                "category": p.category, "sku": p.sku,
            },
        })

    order = Order.objects.create(
        user=user, kind="marketplace", state="draft",
        vendor=items[0][0].vendor,
        rial_amount=total,
        payment_deadline=timezone.now() + __import__("datetime").timedelta(minutes=PAYMENT_DEADLINE_MIN),
        metadata={"shipping_address": shipping_address,
                  "recipient_name": recipient_name,
                  "recipient_phone": recipient_phone},
    )
    for line in line_data:
        OrderItem.objects.create(
            order=order, product=line["product"],
            title_snapshot=line["title"], quantity=line["qty"],
            unit_price_rial=line["unit"], line_total_rial=line["line_total"],
            metadata=line["metadata"],
        )
        line["product"].stock -= line["qty"]
        line["product"].save(update_fields=["stock"])

    from apps.audit.state_machine import order_sm
    order_sm.fire(
        order, trigger="order.submitted",
        actor={"type": "user", "id": str(user.id)},
        target={"type": "order", "id": str(order.id), "owner_id": str(user.id)},
        data={"vendor": str(order.vendor_id), "rial_amount": total,
              "items_count": len(line_data)},
    )
    # If the user has the rial in wallet, settle immediately
    rial = user.rial_wallet
    if rial.available_rial >= total:
        wallet_svc.lock_rial(user, total)
        wallet_svc.unlock_rial(user, total)
        wallet_svc.debit_rial(user, total, kind="adjustment", order=order,
                              description=f"تسویه سفارش {order.order_number}")
        order_sm.fire(order, trigger="payment.verified",
                      target={"type": "order", "id": str(order.id), "owner_id": str(user.id)})
        order_sm.fire(order, trigger="order.process",
                      target={"type": "order", "id": str(order.id), "owner_id": str(user.id)})
        order_sm.fire(order, trigger="order.settle",
                      target={"type": "order", "id": str(order.id), "owner_id": str(user.id)})
        order.paid_at = timezone.now()
        order.save(update_fields=["paid_at"])
    return order
