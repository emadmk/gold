"""Payment endpoints (request + callback)."""
from __future__ import annotations

from django.http import HttpResponseRedirect
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order

from .services import handle_callback, request_payment


class TopupRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            amount = int(request.data.get("amount_rial", 0))
        except (TypeError, ValueError):
            return Response({"detail": "مبلغ نامعتبر"}, status=400)
        if amount < 100_000:
            return Response({"detail": "حداقل شارژ ۱۰۰,۰۰۰ ریال است."}, status=400)
        gateway = request.data.get("gateway", "zarinpal")
        order = Order.objects.create(
            user=request.user, kind="wallet_topup", state="awaiting_payment",
            rial_amount=amount,
        )
        callback = request.build_absolute_uri(f"/api/v1/payments/callback/{gateway}")
        attempt = request_payment(order=order, gateway=gateway, callback_url=callback,
                                  mobile=request.user.phone)
        if attempt.state == "failed":
            return Response({"detail": "خطا در ارتباط با درگاه پرداخت."}, status=502)
        return Response({
            "order_id": str(order.id),
            "order_number": order.order_number,
            "authority": attempt.authority,
            "redirect_url": (attempt.raw_response or {}).get("request", {}).get("redirect_url", ""),
        })


class PaymentCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, gateway: str):
        return self._handle(request, gateway)

    def post(self, request, gateway: str):
        return self._handle(request, gateway)

    def _handle(self, request, gateway: str):
        params = request.GET if request.GET else request.POST
        authority = params.get("Authority") or params.get("authority") or params.get("id") or params.get("refid")
        if not authority:
            return Response({"detail": "پارامتر گم‌شده"}, status=400)
        attempt = handle_callback(gateway=gateway, authority=authority)
        # Redirect to frontend
        if attempt.state == "succeeded":
            return HttpResponseRedirect(f"/orders/{attempt.order_id}?paid=1")
        return HttpResponseRedirect(f"/orders/{attempt.order_id}?paid=0")
