from django.urls import path

from .views import ProductDetailView, ProductListView, VendorDetailView, VendorListView

urlpatterns = [
    path("marketplace/products", ProductListView.as_view()),
    path("marketplace/products/<slug:slug>", ProductDetailView.as_view()),
    path("marketplace/vendors", VendorListView.as_view()),
    path("marketplace/vendors/<slug:shop_slug>", VendorDetailView.as_view()),
]
