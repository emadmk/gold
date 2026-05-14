from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from django.db.models import Q, QuerySet
from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminRole, IsKYCVerified, IsVendor
from apps.orders.serializers import OrderSerializer

from . import cart_services as cart_svc
from .models import Product, Vendor
from .serializers import (
    CartItemSerializer,
    CartSerializer,
    ProductSerializer,
    ShippingAddressSerializer,
    VendorSerializer,
)
from .services import (
    apply_to_vendor,
    approve_vendor,
    checkout,
    compute_product_price,
    suspend_vendor,
)


# ============================================================================
# PLP — filters + sort
# ============================================================================

class ProductListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductSerializer

    def get_queryset(self) -> QuerySet[Product]:
        qs = Product.objects.filter(is_active=True).select_related("vendor")
        q = self.request.query_params

        if cat := q.get("category"):
            qs = qs.filter(category=cat)
        if sub := q.get("sub_category"):
            qs = qs.filter(sub_category_code=sub)
        if brand := q.get("brand"):
            qs = qs.filter(brand__iexact=brand)
        if vendor_slug := q.get("vendor"):
            qs = qs.filter(vendor__shop_slug=vendor_slug)
        if karat := q.get("karat"):
            try:
                qs = qs.filter(karat=int(karat))
            except ValueError:
                pass

        # weight ranges (mg)
        wmin = q.get("weight_mg_min")
        wmax = q.get("weight_mg_max")
        if wmin:
            qs = qs.filter(weight_mg__gte=int(wmin))
        if wmax:
            qs = qs.filter(weight_mg__lte=int(wmax))

        if q.get("in_stock") in ("1", "true", "True"):
            qs = qs.filter(stock__gt=0)

        if search := q.get("q"):
            qs = qs.filter(
                Q(title__icontains=search) | Q(sku__iexact=search)
                | Q(description__icontains=search)
            )

        # Sort ('newest' default; 'cheapest' / 'expensive' / 'bestseller')
        sort = q.get("sort", "newest")
        if sort == "cheapest":
            qs = qs.order_by("fixed_extra_rial", "weight_mg")
        elif sort == "expensive":
            qs = qs.order_by("-weight_mg", "-fixed_extra_rial")
        elif sort == "bestseller":
            qs = qs.order_by("-sold_count", "-created_at")
        else:
            qs = qs.order_by("-created_at")
        return qs

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        # Attach computed_price_rial + low-stock flag per item.
        rows = response.data.get("results") or []
        product_ids = [r["id"] for r in rows]
        prods = {str(p.id): p for p in Product.objects.filter(id__in=product_ids)}
        for r in rows:
            p = prods.get(str(r["id"]))
            if p:
                r["computed_price_rial"] = compute_product_price(p)
        return response


class ProductDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "slug"

    def retrieve(self, request, *args, **kwargs):
        product = self.get_object()
        # Increment view counter (best-effort; race-safe enough)
        Product.objects.filter(pk=product.pk).update(views=product.views + 1)
        data = self.get_serializer(product).data
        data["computed_price_rial"] = compute_product_price(product)
        return Response(data)


# ============================================================================
# Vendor public profile
# ============================================================================

class VendorListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Vendor.objects.filter(state="approved")
    serializer_class = VendorSerializer


class VendorDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    lookup_field = "shop_slug"


# ============================================================================
# Vendor self-service
# ============================================================================

class VendorApplyView(APIView):
    """Multipart onboarding upload of mandatory licenses."""
    permission_classes = [IsAuthenticated, IsKYCVerified]
    parser_classes = [MultiPartParser, FormParser]

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
        return Response(VendorSerializer(request.user.vendor_profile).data)

    def patch(self, request):
        v = request.user.vendor_profile
        for f in ("shop_name", "description", "city", "address", "phone", "iban"):
            if f in request.data:
                setattr(v, f, request.data[f])
        v.save()
        return Response(VendorSerializer(v).data)


class VendorOrdersView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsVendor]

    def get_serializer_class(self):
        return OrderSerializer

    def get_queryset(self):
        from apps.orders.models import Order
        return Order.objects.filter(vendor=self.request.user.vendor_profile).order_by("-created_at")


class VendorSettlementsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsVendor]

    def get_serializer_class(self):
        from rest_framework import serializers as drf_s

        from .settlements import VendorSettlement

        class _S(drf_s.ModelSerializer):
            class Meta:
                model = VendorSettlement
                fields = "__all__"

        return _S

    def get_queryset(self):
        from .settlements import VendorSettlement
        return VendorSettlement.objects.filter(
            vendor=self.request.user.vendor_profile
        ).order_by("-period_end")


class VendorProductsView(generics.ListCreateAPIView):
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


# ============================================================================
# Admin actions
# ============================================================================

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
            suspend_vendor(v, admin=request.user, reason=request.data.get("reason", ""))
        except Exception as exc:  # noqa: BLE001
            return Response({"detail": str(exc)}, status=400)
        return Response(VendorSerializer(v).data)


# ============================================================================
# Cart
# ============================================================================

class CartView(APIView):
    """GET cart + locked-price refresh + totals."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = cart_svc.get_or_create_cart(request.user)
        return Response({
            **CartSerializer(cart).data,
            "lock_state": cart_svc.refresh_locks(cart),
            "totals": cart_svc.cart_totals(cart),
        })

    def delete(self, request):
        cart = cart_svc.get_or_create_cart(request.user)
        cart.items.all().delete()
        cart.discount_code = None
        cart.save(update_fields=["discount_code"])
        return Response({"detail": "سبد خرید پاک شد."})


class CartAddView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = cart_svc.get_or_create_cart(request.user)
        try:
            product = Product.objects.get(id=request.data["product_id"])
        except (KeyError, Product.DoesNotExist):
            return Response({"detail": "محصول یافت نشد."}, status=400)
        qty = int(request.data.get("quantity", 1))
        try:
            item = cart_svc.add_to_cart(cart, product, qty)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)


class CartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id: str):
        cart = cart_svc.get_or_create_cart(request.user)
        qty = int(request.data.get("quantity", 0))
        try:
            cart_svc.update_item(cart, item_id, qty)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)
        except cart.items.model.DoesNotExist:
            return Response({"detail": "آیتم پیدا نشد."}, status=404)
        return Response({"detail": "ok"})

    def delete(self, request, item_id: str):
        cart = cart_svc.get_or_create_cart(request.user)
        cart_svc.remove_item(cart, item_id)
        return Response({"detail": "حذف شد."})


class CartDiscountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = cart_svc.get_or_create_cart(request.user)
        try:
            cart_svc.apply_discount(cart, request.data.get("code"))
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response({
            "totals": cart_svc.cart_totals(cart),
            "discount_code": cart.discount_code.code if cart.discount_code else None,
        })


class CartRelockView(APIView):
    """Refresh every item's lock to the live price (user clicked 'update prices')."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = cart_svc.get_or_create_cart(request.user)
        cart_svc.relock_cart(cart)
        return Response({
            "lock_state": cart_svc.refresh_locks(cart),
            "totals": cart_svc.cart_totals(cart),
        })


# ============================================================================
# Shipping addresses
# ============================================================================

class ShippingAddressListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShippingAddressSerializer

    def get_queryset(self):
        return self.request.user.shipping_addresses.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ShippingAddressDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShippingAddressSerializer
    lookup_field = "id"

    def get_queryset(self):
        return self.request.user.shipping_addresses.all()


class CartShippingAddressView(APIView):
    """Attach a shipping address to the current cart."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from .cart import ShippingAddress

        cart = cart_svc.get_or_create_cart(request.user)
        try:
            addr = ShippingAddress.objects.get(
                id=request.data["address_id"], user=request.user,
            )
        except (KeyError, ShippingAddress.DoesNotExist):
            return Response({"detail": "آدرس یافت نشد."}, status=400)
        cart.shipping_address = addr
        cart.save(update_fields=["shipping_address"])
        return Response({"detail": "آدرس انتخاب شد."})


class CartShippingMethodView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = cart_svc.get_or_create_cart(request.user)
        cart.shipping_method = request.data.get("method", "")
        cart.save(update_fields=["shipping_method"])
        return Response({"detail": "روش ارسال انتخاب شد."})


class CartPaymentMethodView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = cart_svc.get_or_create_cart(request.user)
        method = request.data.get("method", "")
        if method not in ("", "online", "snappay", "gsmpay"):
            return Response({"detail": "روش پرداخت نامعتبر است."}, status=400)
        cart.payment_method = method
        cart.save(update_fields=["payment_method"])
        return Response({"detail": "روش پرداخت انتخاب شد."})


# ============================================================================
# Checkout — finalizes cart into Order
# ============================================================================

class CheckoutView(APIView):
    """Single-call checkout for legacy clients (whole cart in one request)."""
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


class CartCheckoutView(APIView):
    """Multi-step flow: finalize the persistent cart."""
    permission_classes = [IsAuthenticated, IsKYCVerified]

    def post(self, request):
        cart = cart_svc.get_or_create_cart(request.user)
        if not cart.items.exists():
            return Response({"detail": "سبد خرید خالی است."}, status=400)
        if not cart.shipping_address:
            return Response({"detail": "آدرس ارسال انتخاب نشده."}, status=400)
        addr = cart.shipping_address
        items = [(i.product, i.quantity) for i in cart.items.select_related("product")]
        try:
            order = checkout(
                user=request.user, items=items,
                shipping_address=addr.address,
                recipient_name=addr.recipient_name,
                recipient_phone=addr.recipient_phone,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)
        # Empty cart on success
        cart.items.all().delete()
        cart.discount_code = None
        cart.save(update_fields=["discount_code"])
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


# ============================================================================
# Filter facets — for the PLP sidebar UI
# ============================================================================

class PLPFacetsView(APIView):
    """Return min/max weight, brand list, sub-category list for the
    PLP filter sidebar. Fast — single aggregation query."""
    permission_classes = [AllowAny]

    def get(self, request):
        from django.db.models import Max, Min

        qs = Product.objects.filter(is_active=True)
        agg = qs.aggregate(min_w=Min("weight_mg"), max_w=Max("weight_mg"))
        brands = list(qs.exclude(brand="").values_list("brand", flat=True).distinct())
        subs = list(qs.exclude(sub_category_code="")
                      .values_list("sub_category_code", flat=True).distinct())
        return Response({
            "weight_mg_min": agg["min_w"] or 0,
            "weight_mg_max": agg["max_w"] or 0,
            "brands": brands,
            "sub_categories": subs,
            "categories": [c[0] for c in Product.CATEGORIES],
            "karats": [18, 24, 21, 22, 14],
            "weight_buckets": [
                {"label": "زیر ۱ گرم",    "min": 0,     "max": 1000},
                {"label": "۱ تا ۲ گرم",   "min": 1000,  "max": 2000},
                {"label": "۲ تا ۵ گرم",   "min": 2000,  "max": 5000},
                {"label": "۵ تا ۱۰ گرم",  "min": 5000,  "max": 10000},
                {"label": "بیشتر از ۱۰ گرم", "min": 10000, "max": 0},
            ],
        })
