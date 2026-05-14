from rest_framework import serializers

from .models import Product, Vendor


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            "id", "shop_name", "shop_slug", "state", "rating", "total_sales",
            "description", "logo", "city",
        ]
        read_only_fields = fields


class ProductSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "vendor", "category", "title", "slug", "sku",
            "weight_mg", "karat", "manufacturing_fee_pct", "vendor_margin_pct",
            "fixed_extra_rial", "coin_type", "image_urls", "description",
            "stock", "is_active", "created_at",
        ]
