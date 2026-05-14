"""Pricing API views."""
from __future__ import annotations

from django.conf import settings
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PriceTick, SOURCE_KEYS
from .services import issue_quote


class LivePricesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            import redis

            r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        except Exception:  # noqa: BLE001
            r = None
        data: dict[str, int] = {}
        if r is not None:
            for k in SOURCE_KEYS:
                v = r.get(f"price:{k}")
                if v:
                    data[k] = int(v)
        # Fallback to last tick from DB
        for k in SOURCE_KEYS:
            if k in data:
                continue
            tick = PriceTick.objects.filter(source_key=k).order_by("-captured_at").first()
            if tick:
                data[k] = tick.rial_price
        return Response({"data": data})


class QuoteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        asset = request.data.get("asset", "gold")
        side = request.data.get("side", "buy")
        if asset not in ("gold", "silver") or side not in ("buy", "sell"):
            return Response({"detail": "پارامتر نامعتبر"}, status=400)
        quote = issue_quote(user=request.user, asset=asset, side=side)
        return Response({
            "quote_id": str(quote.quote_id),
            "asset": quote.asset,
            "side": quote.side,
            "price_per_mg_rial": quote.price_per_mg_rial,
            "valid_until": quote.valid_until.isoformat(),
        })
