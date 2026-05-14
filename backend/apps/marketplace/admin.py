from django.contrib import admin

from .models import Product, Vendor


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("shop_name", "user", "state", "commission_rate", "rating", "total_sales", "created_at")
    list_filter = ("state",)
    search_fields = ("shop_name", "shop_slug", "user__phone")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "title", "vendor", "category", "weight_mg", "is_active", "stock")
    list_filter = ("category", "is_active")
    search_fields = ("sku", "title", "vendor__shop_name")
