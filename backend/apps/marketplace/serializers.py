from rest_framework import serializers

from .cart import Cart, CartItem, DiscountCode, ShippingAddress
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
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "vendor", "category", "sub_category_code", "brand",
            "title", "slug", "sku",
            "weight_mg", "karat", "manufacturing_fee_pct", "vendor_margin_pct",
            "fixed_extra_rial", "coin_type", "image_urls", "description",
            "stock", "is_low_stock", "is_active", "discount_pct",
            "shipping_cost_rial", "shipping_methods", "metadata",
            "views", "sold_count", "created_at",
        ]


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = [
            "id", "title", "recipient_name", "recipient_phone",
            "recipient_national_id", "province", "city", "address",
            "postal_code", "is_default", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    locked_unit_price_rial = serializers.IntegerField(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "id", "product", "quantity",
            "locked_unit_price_rial", "locked_at", "metadata",
        ]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    shipping_address = ShippingAddressSerializer(read_only=True)
    discount_code = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "id", "items", "discount_code", "shipping_address",
            "shipping_method", "payment_method", "created_at", "updated_at",
        ]

    def get_discount_code(self, obj):
        return obj.discount_code.code if obj.discount_code else None


class DiscountCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCode
        fields = ["code", "kind", "value", "min_order_rial", "max_discount_rial",
                  "valid_from", "valid_until", "description"]
