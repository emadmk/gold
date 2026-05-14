from __future__ import annotations

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsKYCVerified
from apps.pricing.models import PriceQuote

from .models import Order
from .serializers import BuyGoldSerializer, OrderSerializer, SellGoldSerializer
from .services import cancel_order, submit_buy_gold, submit_sell_gold


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


class BuyGoldView(APIView):
    permission_classes = [IsAuthenticated, IsKYCVerified]

    def post(self, request):
        s = BuyGoldSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        quote = PriceQuote.objects.get(quote_id=s.validated_data["quote_id"])
        if quote.asset != "gold" or quote.side != "buy":
            return Response({"detail": "نرخ نامناسب"}, status=400)
        order = submit_buy_gold(user=request.user, quote=quote,
                                mg_amount=s.validated_data["mg_amount"])
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class SellGoldView(APIView):
    permission_classes = [IsAuthenticated, IsKYCVerified]

    def post(self, request):
        s = SellGoldSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        quote = PriceQuote.objects.get(quote_id=s.validated_data["quote_id"])
        if quote.asset != "gold" or quote.side != "sell":
            return Response({"detail": "نرخ نامناسب"}, status=400)
        order = submit_sell_gold(user=request.user, quote=quote,
                                 mg_amount=s.validated_data["mg_amount"])
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):  # noqa: A002
        order = Order.objects.get(id=id, user=request.user)
        cancel_order(order)
        return Response(OrderSerializer(order).data)
