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


@transaction.atomic
def submit_buy_gold(*, user, quote, mg_amount: int) -> Order:
    """Create + submit a buy-gold order, locking the rial cost."""
    if quote.valid_until <= timezone.now():
        raise ValueError("نرخ منقضی شده است؛ مجدداً تأیید کنید.")
    if mg_amount <= 0:
        raise ValueError("مقدار باید بیشتر از صفر باشد.")

    cost = mg_amount * quote.price_per_mg_rial
    order = Order.objects.create(
        user=user,
        kind="buy_gold",
        state="draft",
        quote=quote,
        price_per_mg_rial=quote.price_per_mg_rial,
        mg_amount=mg_amount,
        rial_amount=cost,
        payment_deadline=timezone.now() + timedelta(minutes=PAYMENT_DEADLINE_MIN),
    )
    # If the user has enough rial in-wallet, settle synchronously — no gateway hop.
    rial = user.rial_wallet
    if rial.available_rial >= cost:
        order_sm.fire(
            order, trigger="order.submitted",
            actor={"type": "user", "id": str(user.id)},
            target={"type": "order", "id": str(order.id), "owner_id": str(user.id)},
            data={"asset": "gold", "mg_amount": mg_amount, "rial_amount": cost},
        )
        wallet_svc.lock_rial(user, cost)
        # immediately verify (wallet-funded payment)
        order_sm.fire(order, trigger="payment.verified",
                      actor={"type": "user", "id": str(user.id)},
                      target={"type": "order", "id": str(order.id), "owner_id": str(user.id)})
        complete_buy_order(order)
    else:
        order_sm.fire(
            order, trigger="order.submitted",
            actor={"type": "user", "id": str(user.id)},
            target={"type": "order", "id": str(order.id), "owner_id": str(user.id)},
            data={"asset": "gold", "mg_amount": mg_amount, "rial_amount": cost},
        )
        # rial-locking is conceptual here — payment provider will close the loop
    return order


@transaction.atomic
def submit_sell_gold(*, user, quote, mg_amount: int) -> Order:
    if quote.valid_until <= timezone.now():
        raise ValueError("نرخ منقضی شده است.")
    if mg_amount <= 0:
        raise ValueError("مقدار باید بیشتر از صفر باشد.")
    revenue = mg_amount * quote.price_per_mg_rial

    order = Order.objects.create(
        user=user, kind="sell_gold", state="draft", quote=quote,
        price_per_mg_rial=quote.price_per_mg_rial,
        mg_amount=mg_amount, rial_amount=revenue,
    )
    # debit gold then credit rial — must succeed atomically
    wallet_svc.debit_asset(user, "gold", mg_amount, kind="sell_gold", order=order)
    wallet_svc.credit_rial(user, revenue, kind="adjustment", order=order,
                           description="فروش طلا — درآمد ریالی")
    order_sm.fire(order, trigger="order.submitted",
                  actor={"type": "user", "id": str(user.id)},
                  target={"type": "order", "id": str(order.id), "owner_id": str(user.id)},
                  data={"asset": "gold", "mg_amount": -mg_amount, "rial_amount": revenue})
    order_sm.fire(order, trigger="payment.verified",
                  actor={"type": "user", "id": str(user.id)},
                  target={"type": "order", "id": str(order.id), "owner_id": str(user.id)})
    order_sm.fire(order, trigger="order.process",
                  target={"type": "order", "id": str(order.id), "owner_id": str(user.id)})
    order_sm.fire(order, trigger="order.settle",
                  target={"type": "order", "id": str(order.id), "owner_id": str(user.id)})
    return order


def complete_buy_order(order: Order) -> Order:
    """Move a paid buy_* order to processing then completed; credit asset to wallet."""
    order_sm.fire(order, trigger="order.process",
                  target={"type": "order", "id": str(order.id), "owner_id": str(order.user_id)})

    if order.kind == "buy_gold":
        # debit rial, unlock + remove, credit gold
        try:
            wallet_svc.unlock_rial(order.user, order.rial_amount)
            wallet_svc.debit_rial(order.user, order.rial_amount, kind="adjustment",
                                  order=order, description=f"تسویه سفارش {order.order_number}")
        except InsufficientFunds:
            order_sm.fire(order, trigger="order.fail",
                          target={"type": "order", "id": str(order.id), "owner_id": str(order.user_id)})
            return order
        wallet_svc.credit_asset(order.user, "gold", order.mg_amount, kind="buy_gold", order=order,
                                description=f"خرید طلا — سفارش {order.order_number}")
    elif order.kind == "buy_silver":
        try:
            wallet_svc.unlock_rial(order.user, order.rial_amount)
            wallet_svc.debit_rial(order.user, order.rial_amount, kind="adjustment", order=order)
        except InsufficientFunds:
            order_sm.fire(order, trigger="order.fail",
                          target={"type": "order", "id": str(order.id), "owner_id": str(order.user_id)})
            return order
        wallet_svc.credit_asset(order.user, "silver", order.mg_amount, kind="buy_silver", order=order)
    elif order.kind == "wallet_topup":
        wallet_svc.credit_rial(order.user, order.rial_amount, kind="deposit", order=order,
                               description=f"شارژ کیف پول — سفارش {order.order_number}")

    order_sm.fire(order, trigger="order.settle",
                  target={"type": "order", "id": str(order.id), "owner_id": str(order.user_id)})
    order.paid_at = timezone.now()
    order.save(update_fields=["paid_at"])
    return order


@transaction.atomic
def cancel_order(order: Order) -> Order:
    if order.state != "awaiting_payment":
        raise ValueError("فقط سفارش‌های در انتظار پرداخت لغو می‌شوند.")
    order_sm.fire(order, trigger="order.cancel",
                  actor={"type": "user", "id": str(order.user_id)},
                  target={"type": "order", "id": str(order.id), "owner_id": str(order.user_id)})
    if order.kind in ("buy_gold", "buy_silver"):
        wallet_svc.unlock_rial(order.user, order.rial_amount)
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
