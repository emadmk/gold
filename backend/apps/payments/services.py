"""Payment services: request + verify + idempotent webhook handling."""
from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.audit.emit import emit_event
from apps.audit.models import IdempotencyKey
from apps.audit.state_machine import payment_attempt_sm
from apps.orders.models import Order
from apps.orders.services import complete_buy_order

from .gateways import PaymentRequest, get as get_gateway
from .models import PaymentAttempt


def request_payment(*, order: Order, gateway: str, callback_url: str, mobile: str = "") -> PaymentAttempt:
    gw = get_gateway(gateway)
    attempt = PaymentAttempt.objects.create(
        order=order, gateway=gateway, amount_rial=order.rial_amount, state="pending",
    )
    emit_event(
        "payments.attempt.created",
        actor={"type": "user", "id": str(order.user_id)},
        target={"type": "payment_attempt", "id": str(attempt.id), "owner_id": str(order.user_id)},
        data={"gateway": gateway, "amount_rial": order.rial_amount, "order": order.order_number},
    )
    resp = gw.request(PaymentRequest(
        order_id=order.order_number, amount_rial=order.rial_amount,
        callback_url=callback_url, description=f"KeyhanGold {order.order_number}", mobile=mobile,
    ))
    attempt.raw_response = {"request": resp.__dict__}
    if resp.success:
        attempt.authority = resp.authority
        payment_attempt_sm.fire(attempt, trigger="payment.redirect",
                                target={"type": "payment_attempt", "id": str(attempt.id),
                                        "owner_id": str(order.user_id)},
                                data={"redirect_url": resp.redirect_url})
    else:
        attempt.state = "failed"
        attempt.save(update_fields=["state", "authority", "raw_response"])
        emit_event("payments.attempt.failed", outcome="failure", severity="warning",
                   data={"gateway": gateway, "error": resp.error_message})
    return attempt


def handle_callback(*, gateway: str, authority: str, idempotency_key: str = "") -> PaymentAttempt:
    """Idempotent payment-callback handler.

    The idempotency row is committed in its own transaction so a downstream
    verify failure cannot roll it back; the verification + state change then
    runs in a second atomic block.
    """
    key = idempotency_key or f"{gateway}:{authority}"
    with transaction.atomic():
        if IdempotencyKey.objects.filter(scope="payment.callback", key=key).exists():
            emit_event("payments.webhook.duplicate", severity="warning",
                       data={"gateway": gateway, "authority": authority})
            return PaymentAttempt.objects.get(authority=authority, gateway=gateway)
        IdempotencyKey.objects.create(scope="payment.callback", key=key)

    with transaction.atomic():
        attempt = PaymentAttempt.objects.select_for_update().get(authority=authority, gateway=gateway)
        order = Order.objects.select_for_update().get(id=attempt.order_id)
        if attempt.state == "succeeded":
            return attempt

    emit_event("payments.attempt.callback",
               actor={"type": "gateway", "id": gateway},
               target={"type": "payment_attempt", "id": str(attempt.id),
                       "owner_id": str(order.user_id)})

    gw = get_gateway(gateway)
    verify = gw.verify(authority, attempt.amount_rial)
    attempt.raw_response = {**(attempt.raw_response or {}), "verify": verify.__dict__}
    if verify.success:
        attempt.ref_id = verify.ref_id
        attempt.card_pan_masked = verify.card_pan_masked or ""
        attempt.completed_at = timezone.now()
        payment_attempt_sm.fire(attempt, trigger="payment.verify_ok",
                                target={"type": "payment_attempt", "id": str(attempt.id),
                                        "owner_id": str(order.user_id)})
        order.payment_gateway = gateway
        order.payment_ref = verify.ref_id
        order.save(update_fields=["payment_gateway", "payment_ref"])
        if order.state == "awaiting_payment":
            from apps.audit.state_machine import order_sm
            order_sm.fire(order, trigger="payment.verified",
                          target={"type": "order", "id": str(order.id),
                                  "owner_id": str(order.user_id)})
            complete_buy_order(order)
    else:
        payment_attempt_sm.fire(attempt, trigger="payment.verify_fail",
                                target={"type": "payment_attempt", "id": str(attempt.id),
                                        "owner_id": str(order.user_id)})
    return attempt
