from django.contrib import admin, messages
from django.utils.html import format_html

from apps.audit.state_machine import IllegalTransition

from .models import DeliveryRequest
from .services import transition


@admin.register(DeliveryRequest)
class DeliveryRequestAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "asset", "requested_mg",
                    "state_badge", "tracking_code")
    list_filter = ("state", "asset")
    search_fields = ("user__phone", "tracking_code", "recipient_national_id",
                     "recipient_phone", "recipient_name")
    readonly_fields = ("id", "created_at", "updated_at", "processing_fee_rial")
    date_hierarchy = "created_at"
    fieldsets = (
        ("شناسه", {"fields": ("id", "user", "asset", "requested_mg",
                                "bars_breakdown", "processing_fee_rial")}),
        ("گیرنده", {"fields": ("recipient_name", "recipient_national_id",
                                "recipient_phone", "shipping_address")}),
        ("وضعیت", {"fields": ("state", "tracking_code", "notes")}),
        ("متادیتا", {"fields": ("metadata", "created_at", "updated_at"),
                       "classes": ("collapse",)}),
    )
    actions = ["action_approve", "action_mint", "action_ship", "action_deliver", "action_cancel"]

    @admin.display(description="وضعیت")
    def state_badge(self, obj):
        colors = {
            "pending": "#9CA3AF", "approved": "#2D87F0",
            "minting": "#7C5CFF", "shipped": "#F59E0B",
            "delivered": "#16A34A", "cancelled": "#DC2626",
        }
        c = colors.get(obj.state, "#000")
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px;font-size:11px">{}</span>',
            c, obj.get_state_display(),
        )

    def _bulk_transition(self, request, queryset, trigger, label):
        n = 0
        for d in queryset:
            try:
                transition(d, trigger, actor=request.user)
                n += 1
            except IllegalTransition:
                pass
        self.message_user(request, f"{n} درخواست {label}.", messages.SUCCESS)

    @admin.action(description="تأیید")
    def action_approve(self, request, queryset):
        self._bulk_transition(request, queryset, "delivery.approve", "تأیید شد")

    @admin.action(description="شروع ضرب و پلمپ")
    def action_mint(self, request, queryset):
        self._bulk_transition(request, queryset, "delivery.mint", "به ضرب رفت")

    @admin.action(description="ارسال شد")
    def action_ship(self, request, queryset):
        self._bulk_transition(request, queryset, "delivery.ship", "ارسال شد")

    @admin.action(description="تحویل داده شد")
    def action_deliver(self, request, queryset):
        self._bulk_transition(request, queryset, "delivery.deliver", "تحویل شد")

    @admin.action(description="لغو")
    def action_cancel(self, request, queryset):
        self._bulk_transition(request, queryset, "delivery.cancel", "لغو شد")
