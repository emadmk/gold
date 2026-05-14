"""Price quote service."""
from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from apps.audit.emit import emit_event

from .formulas import gold_buy_per_mg, gold_sell_per_mg, silver_buy_per_mg, silver_sell_per_mg
from .models import PriceQuote, PriceTick


QUOTE_VALIDITY_SECONDS = 6 * 60   # 6 minutes — cart price lock


def latest_tick(source_key: str) -> PriceTick:
    return PriceTick.objects.filter(source_key=source_key).order_by("-captured_at").first()


def issue_quote(*, user, asset: str, side: str) -> PriceQuote:
    if asset == "gold":
        tick = latest_tick("gold_18k_750")
        per_mg = gold_buy_per_mg(tick.rial_price) if side == "buy" else gold_sell_per_mg(tick.rial_price)
    elif asset == "silver":
        tick = latest_tick("silver_999")
        per_mg = silver_buy_per_mg(tick.rial_price) if side == "buy" else silver_sell_per_mg(tick.rial_price)
    else:
        raise ValueError(f"unsupported asset {asset!r}")

    quote = PriceQuote.objects.create(
        user=user,
        asset=asset,
        side=side,
        price_per_mg_rial=per_mg,
        valid_until=timezone.now() + timedelta(seconds=QUOTE_VALIDITY_SECONDS),
        base_tick=tick,
    )
    emit_event(
        "pricing.quote.issued",
        severity="debug",
        actor={"type": "user", "id": str(user.id)} if user else None,
        target={"type": "price_quote", "id": str(quote.quote_id)},
        data={"asset": asset, "side": side, "per_mg": per_mg, "base_rial_per_g": tick.rial_price},
    )
    return quote
