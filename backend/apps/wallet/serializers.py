from rest_framework import serializers

from .models import GoldWallet, RialWallet, WalletTransaction


class RialWalletSerializer(serializers.ModelSerializer):
    available_rial = serializers.IntegerField(read_only=True)

    class Meta:
        model = RialWallet
        fields = ["currency", "balance_rial", "locked_rial", "available_rial", "updated_at"]


class GoldWalletSerializer(serializers.ModelSerializer):
    available_gold_mg = serializers.IntegerField(read_only=True)
    available_silver_mg = serializers.IntegerField(read_only=True)

    class Meta:
        model = GoldWallet
        fields = [
            "address", "balance_mg", "locked_mg", "available_gold_mg",
            "silver_balance_mg", "silver_locked_mg", "available_silver_mg", "updated_at",
        ]


class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = [
            "id", "type", "asset", "rial_amount", "mg_amount",
            "balance_after_rial", "balance_after_mg", "related_order",
            "description", "created_at",
        ]
        read_only_fields = fields
