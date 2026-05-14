from __future__ import annotations

from django.http import FileResponse, Http404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsKYCVerified
from apps.pricing.models import PriceQuote

from .models import Order
from .serializers import BuyGoldSerializer, OrderSerializer, SellGoldSerializer
from .services import (
    cancel_order,
    submit_buy_gold,
    submit_buy_silver,
    submit_sell_gold,
    submit_sell_silver,
)


class OrderListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")


class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


def _trade(request, side: str, asset: str, submit_fn):  # type: ignore[no-untyped-def]
    s = BuyGoldSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    quote = PriceQuote.objects.get(quote_id=s.validated_data["quote_id"])
    if quote.asset != asset or quote.side != side:
        return Response({"detail": "نرخ نامناسب"}, status=400)
    try:
        order = submit_fn(user=request.user, quote=quote,
                          mg_amount=s.validated_data["mg_amount"])
    except ValueError as exc:
        return Response({"detail": str(exc)}, status=400)
    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class BuyGoldView(APIView):
    permission_classes = [IsAuthenticated, IsKYCVerified]

    def post(self, request):
        return _trade(request, "buy", "gold", submit_buy_gold)


class SellGoldView(APIView):
    permission_classes = [IsAuthenticated, IsKYCVerified]

    def post(self, request):
        return _trade(request, "sell", "gold", submit_sell_gold)


class BuySilverView(APIView):
    permission_classes = [IsAuthenticated, IsKYCVerified]

    def post(self, request):
        return _trade(request, "buy", "silver", submit_buy_silver)


class SellSilverView(APIView):
    permission_classes = [IsAuthenticated, IsKYCVerified]

    def post(self, request):
        return _trade(request, "sell", "silver", submit_sell_silver)


class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):  # noqa: A002
        order = Order.objects.get(id=id, user=request.user)
        try:
            cancel_order(order)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response(OrderSerializer(order).data)


class OrderInvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):  # noqa: A002
        try:
            order = Order.objects.get(id=id, user=request.user)
        except Order.DoesNotExist as exc:
            raise Http404 from exc
        if not order.invoice_pdf:
            from .invoices import generate_invoice
            generate_invoice(order)
        if not order.invoice_pdf:
            return Response({"detail": "صدور فاکتور هنوز در دسترس نیست."}, status=404)
        return FileResponse(order.invoice_pdf.open("rb"), content_type="application/pdf")
