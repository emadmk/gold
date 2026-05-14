from django.contrib import admin
from django.utils.html import format_html

from .models import PaymentAttempt


@admin.register(PaymentAttempt)
class PaymentAttemptAdmin(admin.ModelAdmin):
    list_display = ("created_at", "order_number", "gateway", "state_badge", "amount_rial", "ref_id")
    list_filter = ("gateway", "state")
    search_fields = ("authority", "ref_id", "order__order_number")
    readonly_fields = (
        "id", "order", "gateway", "amount_rial",
        "authority", "ref_id", "card_pan_masked", "state",
        "raw_request", "raw_response", "created_at", "completed_at",
    )
    date_hierarchy = "created_at"
    fieldsets = (
        ("شناسه", {"fields": ("id", "order", "gateway")}),
        ("ارقام", {"fields": ("amount_rial", "authority", "ref_id", "card_pan_masked")}),
        ("وضعیت", {"fields": ("state", "created_at", "completed_at")}),
        ("پاسخ خام", {"fields": ("raw_request", "raw_response"), "classes": ("collapse",)}),
    )

    @admin.display(description="سفارش")
    def order_number(self, obj):
        return obj.order.order_number

    @admin.display(description="وضعیت")
    def state_badge(self, obj):
        colors = {
            "pending": "#9CA3AF", "redirected": "#2D87F0",
            "succeeded": "#16A34A", "failed": "#DC2626",
            "cancelled": "#9CA3AF", "expired": "#F59E0B",
        }
        c = colors.get(obj.state, "#000")
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px;font-size:11px">{}</span>',
            c, obj.get_state_display(),
        )
