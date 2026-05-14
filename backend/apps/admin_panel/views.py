"""Aggregated KPI endpoint for the admin Next.js dashboard."""
from __future__ import annotations

from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.accounts.permissions import IsAdminRole
from apps.orders.models import Order
from apps.wallet.models import GoldWallet, RialWallet


class AdminKPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        return Response({
            "users_total": User.objects.count(),
            "users_verified": User.objects.filter(is_verified=True).count(),
            "vendors_total": User.objects.filter(is_vendor=True).count(),
            "orders_today": Order.objects.filter(created_at__date=request.GET.get("date") or None).count(),
            "rial_locked": RialWallet.objects.aggregate(s=Sum("locked_rial"))["s"] or 0,
            "rial_total": RialWallet.objects.aggregate(s=Sum("balance_rial"))["s"] or 0,
            "gold_total_mg": GoldWallet.objects.aggregate(s=Sum("balance_mg"))["s"] or 0,
            "silver_total_mg": GoldWallet.objects.aggregate(s=Sum("silver_balance_mg"))["s"] or 0,
        })
