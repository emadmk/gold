from django.urls import path

from .views import (
    CheckoutView,
    ProductDetailView,
    ProductListView,
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
    path("marketplace/products", ProductListView.as_view()),
    path("marketplace/products/<slug:slug>", ProductDetailView.as_view()),
    path("marketplace/vendors", VendorListView.as_view()),
    path("marketplace/vendors/<slug:shop_slug>", VendorDetailView.as_view()),
    path("marketplace/checkout", CheckoutView.as_view()),
    path("vendor/apply", VendorApplyView.as_view()),
    path("vendor/me", VendorMeView.as_view()),
    path("vendor/products", VendorProductsView.as_view()),
    path("vendor/orders", VendorOrdersView.as_view()),
    path("vendor/settlements", VendorSettlementsView.as_view()),
    path("admin/vendors/<uuid:vendor_id>/approve", VendorAdminApproveView.as_view()),
    path("admin/vendors/<uuid:vendor_id>/suspend", VendorAdminSuspendView.as_view()),
]
