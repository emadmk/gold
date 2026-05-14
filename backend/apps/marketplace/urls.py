from django.urls import path

from .views import (
    CartAddView,
    CartCheckoutView,
    CartDiscountView,
    CartItemView,
    CartPaymentMethodView,
    CartRelockView,
    CartShippingAddressView,
    CartShippingMethodView,
    CartView,
    CheckoutView,
    PLPFacetsView,
    ProductDetailView,
    ProductListView,
    ShippingAddressDetail,
    ShippingAddressListCreate,
    VendorAdminApproveView,
    VendorAdminSuspendView,
    VendorApplyView,
    VendorDetailView,
    VendorListView,
    VendorMeView,
    VendorOrdersView,
    VendorProductsView,
    VendorSettlementsView,
)

urlpatterns = [
    # Public catalogue (SSR consumers)
    path("marketplace/products", ProductListView.as_view()),
    path("marketplace/products/<slug:slug>", ProductDetailView.as_view()),
    path("marketplace/facets", PLPFacetsView.as_view()),
    path("marketplace/vendors", VendorListView.as_view()),
    path("marketplace/vendors/<slug:shop_slug>", VendorDetailView.as_view()),
    # Legacy single-call checkout (kept for backwards compat)
    path("marketplace/checkout", CheckoutView.as_view()),
    # Cart (server-side, 6-min price-lock)
    path("cart", CartView.as_view()),
    path("cart/items", CartAddView.as_view()),
    path("cart/items/<uuid:item_id>", CartItemView.as_view()),
    path("cart/discount", CartDiscountView.as_view()),
    path("cart/relock", CartRelockView.as_view()),
    path("cart/shipping/address", CartShippingAddressView.as_view()),
    path("cart/shipping/method", CartShippingMethodView.as_view()),
    path("cart/payment-method", CartPaymentMethodView.as_view()),
    path("cart/checkout", CartCheckoutView.as_view()),
    # Shipping addresses CRUD
    path("addresses", ShippingAddressListCreate.as_view()),
    path("addresses/<uuid:id>", ShippingAddressDetail.as_view()),
    # Vendor self-service
    path("vendor/apply", VendorApplyView.as_view()),
    path("vendor/me", VendorMeView.as_view()),
    path("vendor/products", VendorProductsView.as_view()),
    path("vendor/orders", VendorOrdersView.as_view()),
    path("vendor/settlements", VendorSettlementsView.as_view()),
    # Admin actions
    path("admin/vendors/<uuid:vendor_id>/approve", VendorAdminApproveView.as_view()),
    path("admin/vendors/<uuid:vendor_id>/suspend", VendorAdminSuspendView.as_view()),
]
