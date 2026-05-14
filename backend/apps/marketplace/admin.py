from django.contrib import admin, messages
from django.utils.html import format_html

from apps.audit.state_machine import IllegalTransition

from .models import Product, Vendor
from .services import approve_vendor, suspend_vendor
from .settlements import VendorSettlement


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = (
        "shop_name", "user", "state_badge", "commission_rate",
        "rating", "total_sales", "city", "created_at",
    )
    list_filter = ("state", "city", "tenant_id")
    search_fields = ("shop_name", "shop_slug", "legal_name", "user__phone")
    readonly_fields = ("id", "created_at", "rating", "total_sales")
    fieldsets = (
        ("هویت", {"fields": ("id", "user", "shop_name", "shop_slug", "legal_name", "logo")}),
        ("مدارک", {"fields": ("business_license", "union_license")}),
        ("مالی", {"fields": ("iban", "commission_rate")}),
        ("وضعیت", {"fields": ("state", "rating", "total_sales")}),
        ("نشانی", {"fields": ("city", "address", "phone")}),
        ("توضیحات", {"fields": ("description", "metadata", "created_at")}),
    )
    actions = ["action_approve", "action_suspend"]

    @admin.display(description="وضعیت")
    def state_badge(self, obj):
        colors = {"applied": "#F59E0B", "approved": "#16A34A",
                  "suspended": "#DC2626", "rejected": "#6B7280"}
        c = colors.get(obj.state, "#000")
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px;font-size:11px">{}</span>',
            c, obj.get_state_display(),
        )

    @admin.action(description="تأیید فروشنده‌های انتخاب‌شده")
    def action_approve(self, request, queryset):
        n = 0
        for v in queryset.filter(state="applied"):
            try:
                approve_vendor(v, admin=request.user)
                n += 1
            except IllegalTransition:
                pass
        self.message_user(request, f"{n} فروشنده تأیید شد.", messages.SUCCESS)

    @admin.action(description="تعلیق فروشنده‌های انتخاب‌شده")
    def action_suspend(self, request, queryset):
        n = 0
        for v in queryset.filter(state="approved"):
            try:
                suspend_vendor(v, admin=request.user, reason="from admin action")
                n += 1
            except IllegalTransition:
                pass
        self.message_user(request, f"{n} فروشنده تعلیق شد.", messages.WARNING)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "title", "vendor", "category", "karat",
                    "weight_mg", "stock", "is_active")
    list_filter = ("category", "is_active", "karat", "vendor__state")
    search_fields = ("sku", "title", "vendor__shop_name", "vendor__shop_slug")
    readonly_fields = ("id", "created_at")
    fieldsets = (
        ("فروشنده و دسته", {"fields": ("vendor", "category", "coin_type")}),
        ("هویت", {"fields": ("id", "title", "slug", "sku", "description", "image_urls")}),
        ("مشخصات", {"fields": ("weight_mg", "karat", "manufacturing_fee_pct",
                                "vendor_margin_pct", "fixed_extra_rial")}),
        ("موجودی", {"fields": ("stock", "is_active")}),
        ("متادیتا", {"fields": ("metadata", "created_at"), "classes": ("collapse",)}),
    )


@admin.register(VendorSettlement)
class VendorSettlementAdmin(admin.ModelAdmin):
    list_display = ("vendor", "period_end", "orders_count",
                    "gross_rial", "commission_rial", "net_rial", "paid_at")
    list_filter = ("vendor",)
    date_hierarchy = "period_end"
    readonly_fields = tuple(f.name for f in VendorSettlement._meta.fields)
