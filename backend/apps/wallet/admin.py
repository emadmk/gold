from django.contrib import admin
from django.utils.html import format_html

from .models import GoldWallet, RialWallet, WalletTransaction


@admin.register(RialWallet)
class RialWalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance_toman", "locked_toman", "available_toman",
                    "currency", "updated_at")
    list_filter = ("currency", "tenant_id")
    search_fields = ("user__phone",)
    readonly_fields = tuple(f.name for f in RialWallet._meta.fields)

    @admin.display(description="موجودی (تومان)")
    def balance_toman(self, obj):
        return f"{obj.balance_rial // 10:,}"

    @admin.display(description="قفل‌شده (تومان)")
    def locked_toman(self, obj):
        return f"{obj.locked_rial // 10:,}"

    @admin.display(description="قابل برداشت (تومان)")
    def available_toman(self, obj):
        return f"{obj.available_rial // 10:,}"


@admin.register(GoldWallet)
class GoldWalletAdmin(admin.ModelAdmin):
    list_display = ("user", "address_short", "gold_g", "silver_g", "updated_at")
    search_fields = ("user__phone", "address")
    readonly_fields = tuple(f.name for f in GoldWallet._meta.fields)

    @admin.display(description="آدرس")
    def address_short(self, obj):
        return format_html('<code>{}</code>', obj.address)

    @admin.display(description="طلا (گرم)")
    def gold_g(self, obj):
        return f"{obj.balance_mg / 1000:.3f}"

    @admin.display(description="نقره (گرم)")
    def silver_g(self, obj):
        return f"{obj.silver_balance_mg / 1000:.3f}"


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "type", "asset",
                    "rial_amount", "mg_amount", "related_order", "event_id_short")
    list_filter = ("type", "asset")
    search_fields = ("user__phone", "event_id", "related_order__order_number",
                     "description")
    date_hierarchy = "created_at"
    readonly_fields = tuple(f.name for f in WalletTransaction._meta.fields)

    @admin.display(description="event")
    def event_id_short(self, obj):
        return obj.event_id[:8] if obj.event_id else "—"

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False
