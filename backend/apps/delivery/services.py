"""Delivery request service."""
from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import transaction

from apps.audit.state_machine import delivery_sm
from apps.wallet import services as wallet_svc

from .models import DeliveryRequest


@transaction.atomic
def request_delivery(*, user, mg: int, address: str, name: str, nid: str, phone: str,
                     bars: dict | None = None) -> DeliveryRequest:
    fee_pct = Decimal(settings.DOMAIN_DEFAULTS["delivery_processing_fee_pct"])
    min_mg = int(Decimal(settings.DOMAIN_DEFAULTS["min_physical_delivery_mg"]))
    if mg < min_mg:
        raise ValueError(f"حداقل وزن تحویل {min_mg} میلی‌گرم است.")
    # Estimate the fee using the latest gold tick — best effort
    from apps.pricing.models import PriceTick
    tick = PriceTick.objects.filter(source_key="gold_18k_750").order_by("-captured_at").first()
    rial_value = (mg * (tick.rial_price if tick else 0)) // 1000
    fee = int(Decimal(rial_value) * fee_pct)
    # burn gold and rial fee
    wallet_svc.debit_asset(user, "gold", mg, kind="delivery_burn",
                           description="تحویل فیزیکی")
    if fee > 0:
        wallet_svc.debit_rial(user, fee, kind="commission",
                              description="کارمزد ضرب و پلمپ تحویل فیزیکی")
    req = DeliveryRequest.objects.create(
        user=user, asset="gold", requested_mg=mg,
        bars_breakdown=bars or {}, processing_fee_rial=fee,
        shipping_address=address, recipient_name=name,
        recipient_national_id=nid, recipient_phone=phone,
    )
    return req


def transition(req: DeliveryRequest, trigger: str, actor=None) -> DeliveryRequest:
    delivery_sm.fire(
        req, trigger=trigger,
        actor={"type": "admin", "id": str(actor.id)} if actor else None,
        target={"type": "delivery", "id": str(req.id), "owner_id": str(req.user_id)},
    )
    return req
