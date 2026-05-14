from __future__ import annotations

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminRole, IsKYCVerified, IsVendor
from apps.orders.serializers import OrderSerializer

from .models import Product, Vendor
from .serializers import ProductSerializer, VendorSerializer
from .services import (
    apply_to_vendor,
    approve_vendor,
    checkout,
    compute_product_price,
    suspend_vendor,
)


class ProductListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Product.objects.filter(is_active=True).select_related("vendor")
    serializer_class = ProductSerializer


class ProductDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "slug"

    def retrieve(self, request, *args, **kwargs):
        product = self.get_object()
        data = self.get_serializer(product).data
        data["computed_price_rial"] = compute_product_price(product)
        return Response(data)


class VendorListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Vendor.objects.filter(state="approved")
    serializer_class = VendorSerializer


class VendorDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    lookup_field = "shop_slug"


class VendorApplyView(APIView):
    """Vendor onboarding — multipart upload of mandatory licenses."""

    permission_classes = [IsAuthenticated, IsKYCVerified]
    parser_classes = [
        __import__("rest_framework.parsers", fromlist=["MultiPartParser"]).MultiPartParser,
        __import__("rest_framework.parsers", fromlist=["FormParser"]).FormParser,
    ]

    def post(self, request):
        from django.core.exceptions import ValidationError

        from apps.security.uploads import DEFAULT_DOC_MIMES, validate_upload

        try:
            v = apply_to_vendor(
                user=request.user,
                shop_name=request.data.get("shop_name", ""),
                shop_slug=request.data.get("shop_slug", ""),
                legal_name=request.data.get("legal_name", ""),
                iban=request.data.get("iban", ""),
                city=request.data.get("city", ""),
                description=request.data.get("description", ""),
            )
            for field in ("business_license", "union_license", "logo"):
                f = request.FILES.get(field)
                if f:
                    validate_upload(f, allowed_mimes=DEFAULT_DOC_MIMES)
                    setattr(v, field, f)
            v.save()
        except ValidationError as exc:
            return Response({"detail": exc.messages[0]}, status=400)
        except Exception as exc:  # noqa: BLE001
            return Response({"detail": str(exc)}, status=400)
        return Response(VendorSerializer(v).data, status=status.HTTP_201_CREATED)


class VendorMeView(APIView):
    permission_classes = [IsAuthenticated, IsVendor]

    def get(self, request):
        v = request.user.vendor_profile
        return Response(VendorSerializer(v).data)

    def patch(self, request):
        v = request.user.vendor_profile
        for f in ("shop_name", "description", "city", "address", "phone", "iban"):
            if f in request.data:
                setattr(v, f, request.data[f])
        v.save()
        return Response(VendorSerializer(v).data)


class VendorOrdersView(generics.ListAPIView):
    """Orders received by the logged-in vendor."""

    permission_classes = [IsAuthenticated, IsVendor]

    def get_serializer_class(self):
        from apps.orders.serializers import OrderSerializer
        return OrderSerializer

    def get_queryset(self):
        from apps.orders.models import Order
        return Order.objects.filter(vendor=self.request.user.vendor_profile).order_by("-created_at")


class VendorSettlementsView(generics.ListAPIView):
    """Settlements paid to the logged-in vendor."""

    permission_classes = [IsAuthenticated, IsVendor]

    def get_serializer_class(self):
        from rest_framework import serializers as drf_s

        from .settlements import VendorSettlement

        class _Ser(drf_s.ModelSerializer):
            class Meta:
                model = VendorSettlement
                fields = "__all__"

        return _Ser

    def get_queryset(self):
        from .settlements import VendorSettlement
        return VendorSettlement.objects.filter(vendor=self.request.user.vendor_profile).order_by("-period_end")


class VendorAdminApproveView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, vendor_id: str):
        v = Vendor.objects.get(id=vendor_id)
        try:
            approve_vendor(v, admin=request.user)
        except Exception as exc:  # noqa: BLE001
            return Response({"detail": str(exc)}, status=400)
        return Response(VendorSerializer(v).data)


class VendorAdminSuspendView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, vendor_id: str):
        v = Vendor.objects.get(id=vendor_id)
        try:
            suspend_vendor(v, admin=request.user,
                           reason=request.data.get("reason", ""))
        except Exception as exc:  # noqa: BLE001
            return Response({"detail": str(exc)}, status=400)
        return Response(VendorSerializer(v).data)


class VendorProductsView(generics.ListCreateAPIView):
    """The logged-in vendor's product CRUD."""

    permission_classes = [IsAuthenticated, IsVendor]
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(vendor=self.request.user.vendor_profile)

    def perform_create(self, serializer):
        from apps.audit.emit import emit_event

        prod = serializer.save(vendor=self.request.user.vendor_profile)
        emit_event(
            "marketplace.product.published",
            actor={"type": "vendor", "id": str(prod.vendor_id)},
            target={"type": "product", "id": str(prod.id)},
        )


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated, IsKYCVerified]

    def post(self, request):
        raw_items = request.data.get("items", [])
        items = []
        for line in raw_items:
            try:
                p = Product.objects.get(id=line["product_id"])
            except (KeyError, Product.DoesNotExist):
                return Response({"detail": "محصول یافت نشد."}, status=400)
            qty = int(line.get("quantity", 1))
            items.append((p, qty))
        try:
            order = checkout(
                user=request.user, items=items,
                shipping_address=request.data.get("shipping_address", ""),
                recipient_name=request.data.get("recipient_name", ""),
                recipient_phone=request.data.get("recipient_phone", ""),
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
