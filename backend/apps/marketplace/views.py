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
    permission_classes = [IsAuthenticated, IsKYCVerified]

    def post(self, request):
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
        except Exception as exc:  # noqa: BLE001
            return Response({"detail": str(exc)}, status=400)
        return Response(VendorSerializer(v).data, status=status.HTTP_201_CREATED)


class VendorMeView(APIView):
    permission_classes = [IsAuthenticated, IsVendor]

    def get(self, request):
        v = request.user.vendor_profile
        return Response(VendorSerializer(v).data)


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
