from django.contrib import admin, messages
from django.utils.html import format_html

from apps.audit.state_machine import IllegalTransition

from .models import Order, OrderItem
from .services import cancel_order, complete_buy_order, expire_order


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("title_snapshot", "quantity", "unit_price_rial", "line_total_rial", "metadata")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number", "user", "kind", "state_badge",
        "rial_amount", "mg_amount", "payment_gateway", "created_at",
    )
    list_filter = ("kind", "state", "payment_gateway", "tenant_id")
    search_fields = ("order_number", "user__phone", "payment_ref", "vendor__shop_name")
    inlines = [OrderItemInline]
    readonly_fields = (
        "id", "order_number", "quote", "price_per_mg_rial", "mg_amount",
        "rial_amount", "commission_rial", "commission_mg",
        "payment_deadline", "payment_gateway", "payment_ref",
        "paid_at", "vendor", "invoice_pdf", "metadata", "created_at", "updated_at",
    )
    fieldsets = (
        ("شناسه", {"fields": ("id", "order_number", "tenant_id", "user")}),
        ("نوع و وضعیت", {"fields": ("kind", "state")}),
        ("ارقام", {"fields": ("quote", "price_per_mg_rial", "mg_amount", "rial_amount",
                                  "commission_rial", "commission_mg")}),
        ("پرداخت", {"fields": ("payment_deadline", "payment_gateway", "payment_ref", "paid_at")}),
        ("مارکت‌پلیس", {"fields": ("vendor", "invoice_pdf"), "classes": ("collapse",)}),
        ("متادیتا", {"fields": ("metadata", "created_at", "updated_at"), "classes": ("collapse",)}),
    )
    date_hierarchy = "created_at"
    actions = ["action_cancel", "action_expire", "action_settle"]

    @admin.display(description="وضعیت")
    def state_badge(self, obj):
        colors = {
            "draft": "#6B7280", "awaiting_payment": "#F59E0B",
            "paid": "#2D87F0", "processing": "#7C5CFF",
            "completed": "#16A34A", "expired": "#9CA3AF",
            "cancelled": "#9CA3AF", "refunded": "#9CA3AF",
            "failed": "#DC2626",
        }
        c = colors.get(obj.state, "#000")
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px;font-size:11px">{}</span>',
            c, obj.get_state_display(),
        )

    @admin.action(description="لغو سفارش‌های انتخاب‌شده")
    def action_cancel(self, request, queryset):
        n = 0
        for o in queryset:
            try:
                cancel_order(o)
                n += 1
            except (ValueError, IllegalTransition):
                pass
        self.message_user(request, f"{n} سفارش لغو شد.", messages.SUCCESS)

    @admin.action(description="انقضای سفارش‌های انتخاب‌شده")
    def action_expire(self, request, queryset):
        n = 0
        for o in queryset.filter(state="awaiting_payment"):
            try:
                expire_order(o)
                n += 1
            except IllegalTransition:
                pass
        self.message_user(request, f"{n} سفارش منقضی شد.", messages.SUCCESS)

    @admin.action(description="تسویه دستی سفارش‌های پرداخت‌شده")
    def action_settle(self, request, queryset):
        n = 0
        for o in queryset.filter(state="paid"):
            try:
                complete_buy_order(o)
                n += 1
            except IllegalTransition:
                pass
        self.message_user(request, f"{n} سفارش تسویه شد.", messages.SUCCESS)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "title_snapshot", "quantity", "unit_price_rial", "line_total_rial")
    search_fields = ("order__order_number", "title_snapshot")
    readonly_fields = ("order", "product", "title_snapshot", "quantity",
                       "unit_price_rial", "line_total_rial", "metadata")
