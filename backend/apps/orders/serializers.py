from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product", "title_snapshot", "quantity", "unit_price_rial", "line_total_rial", "metadata"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "order_number", "kind", "state",
            "price_per_mg_rial", "mg_amount", "rial_amount",
            "commission_rial", "commission_mg",
            "payment_deadline", "payment_gateway", "paid_at",
            "vendor", "invoice_pdf", "items", "created_at", "updated_at", "metadata",
        ]
        read_only_fields = fields


class BuyGoldSerializer(serializers.Serializer):
    quote_id = serializers.UUIDField()
    mg_amount = serializers.IntegerField(min_value=1)


class SellGoldSerializer(BuyGoldSerializer):
    pass
