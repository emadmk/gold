from django.contrib import admin

from .models import GoldWallet, RialWallet, WalletTransaction


@admin.register(RialWallet)
class RialWalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance_rial", "locked_rial", "currency", "updated_at")
    search_fields = ("user__phone",)


@admin.register(GoldWallet)
class GoldWalletAdmin(admin.ModelAdmin):
    list_display = ("user", "address", "balance_mg", "silver_balance_mg", "updated_at")
    search_fields = ("user__phone", "address")


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "type", "asset", "rial_amount", "mg_amount")
    list_filter = ("type", "asset")
    search_fields = ("user__phone", "event_id")
    readonly_fields = ("event_id", "balance_after_rial", "balance_after_mg")
