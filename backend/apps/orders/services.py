"""Order lifecycle services — every mutation goes through the SM."""
from __future__ import annotations

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.audit.state_machine import order_sm
from apps.wallet import services as wallet_svc
from apps.wallet.services import InsufficientFunds

from .models import Order


PAYMENT_DEADLINE_MIN = 30


def _submit_trade(*, user, quote, mg_amount: int, asset: str, side: str) -> Order:
    """Shared logic for gold/silver buy/sell. side ∈ {buy, sell}."""
    if quote.valid_until <= timezone.now():
        raise ValueError("نرخ منقضی شده است؛ مجدداً تأیید کنید.")
    if mg_amount <= 0:
        raise ValueError("مقدار باید بیشتر از صفر باشد.")
    if quote.asset != asset or quote.side != side:
        raise ValueError("نرخ با نوع سفارش هم‌خوانی ندارد.")

    rial_value = mg_amount * quote.price_per_mg_rial
    kind = f"{side}_{asset}"
    order = Order.objects.create(
        user=user,
        kind=kind,
        state="draft",
        quote=quote,
        price_per_mg_rial=quote.price_per_mg_rial,
        mg_amount=mg_amount,
        rial_amount=rial_value,
        payment_deadline=timezone.now() + timedelta(minutes=PAYMENT_DEADLINE_MIN),
    )

    if side == "buy":
        # Re-fetch — `user.rial_wallet` may be cached on the user.
        from apps.wallet.models import RialWallet

        rial = RialWallet.objects.get(user=user)
        if rial.available_rial >= rial_value:
            order_sm.fire(
                order, trigger="order.submitted",
                actor={"type": "user", "id": str(user.id)},
                target={"type": "order", "id": str(order.id), "owner_id": str(user.id)},
                data={"asset": asset, "mg_amount": mg_amount, "rial_amount": rial_value},
            )
            wallet_svc.lock_rial(user, rial_value)
            order_sm.fire(order, trigger="payment.verified",
                          actor={"type": "user", "id": str(user.id)},
                          target={"type": "order", "id": str(order.id), "owner_id": str(user.id)})
            complete_buy_order(order)
        else:
            order_sm.fire(
                order, trigger="order.submitted",
                actor={"type": "user", "id": str(user.id)},
                target={"type": "order", "id": str(order.id), "owner_id": str(user.id)},
                data={"asset": asset, "mg_amount": mg_amount, "rial_amount": rial_value},
            )
    else:  # sell
        wallet_svc.debit_asset(user, asset, mg_amount, kind=kind, order=order)
        wallet_svc.credit_rial(user, rial_value, kind="adjustment", order=order,
                               description=f"فروش {asset} — درآمد ریالی")
        order_sm.fire(order, trigger="order.submitted",
                      actor={"type": "user", "id": str(user.id)},
                      target={"type": "order", "id": str(order.id), "owner_id": str(user.id)},
                      data={"asset": asset, "mg_amount": -mg_amount, "rial_amount": rial_value})
        order_sm.fire(order, trigger="payment.verified",
                      actor={"type": "user", "id": str(user.id)},
                      target={"type": "order", "id": str(order.id), "owner_id": str(user.id)})
        order_sm.fire(order, trigger="order.process",
                      target={"type": "order", "id": str(order.id), "owner_id": str(user.id)})
        order_sm.fire(order, trigger="order.settle",
                      target={"type": "order", "id": str(order.id), "owner_id": str(user.id)})
    return order


@transaction.atomic
def submit_buy_gold(*, user, quote, mg_amount: int) -> Order:
    return _submit_trade(user=user, quote=quote, mg_amount=mg_amount, asset="gold", side="buy")


@transaction.atomic
def submit_sell_gold(*, user, quote, mg_amount: int) -> Order:
    return _submit_trade(user=user, quote=quote, mg_amount=mg_amount, asset="gold", side="sell")


@transaction.atomic
def submit_buy_silver(*, user, quote, mg_amount: int) -> Order:
    return _submit_trade(user=user, quote=quote, mg_amount=mg_amount, asset="silver", side="buy")


@transaction.atomic
def submit_sell_silver(*, user, quote, mg_amount: int) -> Order:
    return _submit_trade(user=user, quote=quote, mg_amount=mg_amount, asset="silver", side="sell")


def complete_buy_order(order: Order) -> Order:
    """Move a paid buy_* / topup order to processing then completed."""
    order_sm.fire(order, trigger="order.process",
                  target={"type": "order", "id": str(order.id), "owner_id": str(order.user_id)})

    if order.kind in ("buy_gold", "buy_silver"):
        asset = "gold" if order.kind == "buy_gold" else "silver"
        try:
            wallet_svc.unlock_rial(order.user, order.rial_amount)
            wallet_svc.debit_rial(order.user, order.rial_amount, kind="adjustment",
                                  order=order, description=f"تسویه سفارش {order.order_number}")
        except InsufficientFunds:
            order_sm.fire(order, trigger="order.fail",
                          target={"type": "order", "id": str(order.id), "owner_id": str(order.user_id)})
            return order
        wallet_svc.credit_asset(order.user, asset, order.mg_amount, kind=order.kind, order=order,
                                description=f"خرید {asset} — سفارش {order.order_number}")
    elif order.kind == "wallet_topup":
        wallet_svc.credit_rial(order.user, order.rial_amount, kind="deposit", order=order,
                               description=f"شارژ کیف پول — سفارش {order.order_number}")

    order_sm.fire(order, trigger="order.settle",
                  target={"type": "order", "id": str(order.id), "owner_id": str(order.user_id)})
    order.paid_at = timezone.now()
    order.save(update_fields=["paid_at"])
    # Generate invoice PDF asynchronously
    try:
        from .invoices import generate_invoice
        generate_invoice(order)
    except Exception:  # noqa: BLE001 — never block settlement
        pass
    return order


@transaction.atomic
def cancel_order(order: Order) -> Order:
    if order.state != "awaiting_payment":
        raise ValueError("فقط سفارش‌های در انتظار پرداخت لغو می‌شوند.")
    order_sm.fire(order, trigger="order.cancel",
                  actor={"type": "user", "id": str(order.user_id)},
                  target={"type": "order", "id": str(order.id), "owner_id": str(order.user_id)})
    if order.kind in ("buy_gold", "buy_silver"):
        try:
            wallet_svc.unlock_rial(order.user, order.rial_amount)
        except Exception:  # noqa: BLE001
            pass
    return order


@transaction.atomic
def expire_order(order: Order) -> Order:
    order_sm.fire(order, trigger="order.timeout",
                  target={"type": "order", "id": str(order.id), "owner_id": str(order.user_id)})
    if order.kind in ("buy_gold", "buy_silver"):
        try:
            wallet_svc.unlock_rial(order.user, order.rial_amount)
        except Exception:  # noqa: BLE001
            pass
    return order
