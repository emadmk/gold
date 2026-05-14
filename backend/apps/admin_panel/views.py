"""Aggregated KPI endpoints + admin-only operations for the Next.js panel."""
from __future__ import annotations

from decimal import Decimal

from django.db.models import Sum
from rest_framework import generics, serializers as drf_s, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import KYCSubmission, User
from apps.accounts.permissions import IsAdminRole
from apps.accounts.serializers import KYCSubmissionSerializer, UserSerializer
from apps.audit.emit import emit_event
from apps.audit.models import AuditEntry
from apps.marketplace.models import Vendor
from apps.marketplace.serializers import VendorSerializer
from apps.marketplace.settlements import VendorSettlement
from apps.orders.models import Order
from apps.orders.serializers import OrderSerializer
from apps.pricing.models import PricingFormula
from apps.wallet.models import GoldWallet, RialWallet


class AdminKPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        return Response({
            "users_total": User.objects.count(),
            "users_verified": User.objects.filter(is_verified=True).count(),
            "vendors_total": Vendor.objects.filter(state="approved").count(),
            "orders_total": Order.objects.count(),
            "rial_locked": RialWallet.objects.aggregate(s=Sum("locked_rial"))["s"] or 0,
            "rial_total": RialWallet.objects.aggregate(s=Sum("balance_rial"))["s"] or 0,
            "gold_total_mg": GoldWallet.objects.aggregate(s=Sum("balance_mg"))["s"] or 0,
            "silver_total_mg": GoldWallet.objects.aggregate(s=Sum("silver_balance_mg"))["s"] or 0,
        })


class AdminKYCQueueView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    serializer_class = KYCSubmissionSerializer
    queryset = KYCSubmission.objects.exclude(state__in=("approved", "rejected"))


class AdminUsersView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by("-created_at")


class AdminVendorsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    serializer_class = VendorSerializer
    queryset = Vendor.objects.all().order_by("-created_at")


class AdminOrdersView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    serializer_class = OrderSerializer
    queryset = Order.objects.all().order_by("-created_at")


class FreezeUserView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, user_id: str):
        u = User.objects.get(id=user_id)
        u.is_frozen = True
        u.save(update_fields=["is_frozen"])
        emit_event(
            "accounts.user.frozen", severity="critical",
            actor={"type": "admin", "id": str(request.user.id)},
            target={"type": "user", "id": str(u.id)},
            data={"reason": request.data.get("reason", "")},
        )
        return Response({"detail": "کاربر مسدود شد."})


class UnfreezeUserView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, user_id: str):
        u = User.objects.get(id=user_id)
        u.is_frozen = False
        u.save(update_fields=["is_frozen"])
        return Response({"detail": "حساب کاربر بازفعال شد."})


class _PricingFormulaSerializer(drf_s.ModelSerializer):
    class Meta:
        model = PricingFormula
        fields = ["key", "value", "description", "updated_at"]


class AdminFormulasView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        return Response(
            _PricingFormulaSerializer(PricingFormula.objects.all(), many=True).data
        )

    def put(self, request):
        for row in request.data:
            try:
                value = Decimal(str(row["value"]))
            except Exception:  # noqa: BLE001
                return Response({"detail": f"value نامعتبر برای {row.get('key')}"}, status=400)
            obj, _ = PricingFormula.objects.update_or_create(
                key=row["key"],
                defaults={"value": value, "updated_by": request.user,
                          "description": row.get("description", "")},
            )
            emit_event(
                "pricing.formula.updated",
                actor={"type": "admin", "id": str(request.user.id)},
                target={"type": "pricing_formula", "id": obj.key},
                data={"value": str(value)},
            )
        return Response({"detail": "فرمول‌ها به‌روزرسانی شد."},
                        status=status.HTTP_200_OK)


class _SettlementSerializer(drf_s.ModelSerializer):
    class Meta:
        model = VendorSettlement
        fields = "__all__"


class AdminSettlementsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = VendorSettlement.objects.all().order_by("-period_end")
    serializer_class = _SettlementSerializer


class _AuditSerializer(drf_s.ModelSerializer):
    class Meta:
        model = AuditEntry
        fields = "__all__"


class AdminAuditLogView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = AuditEntry.objects.all().order_by("-created_at")
    serializer_class = _AuditSerializer
