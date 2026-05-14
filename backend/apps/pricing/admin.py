from django.contrib import admin, messages

from apps.audit.emit import emit_event

from .models import PriceQuote, PriceTick, PricingFormula
from .tasks import crawl_all


@admin.register(PriceTick)
class PriceTickAdmin(admin.ModelAdmin):
    list_display = ("source_key", "rial_price", "captured_at", "source")
    list_filter = ("source_key", "source")
    search_fields = ("source_key",)
    date_hierarchy = "captured_at"
    readonly_fields = tuple(f.name for f in PriceTick._meta.fields)
    actions = ["action_crawl_now"]

    @admin.action(description="کرال فوری همه قیمت‌ها از TGJU")
    def action_crawl_now(self, request, queryset):  # noqa: ARG002
        try:
            result = crawl_all()
            self.message_user(request, f"کرال انجام شد: {result}",
                              messages.SUCCESS)
        except Exception as exc:  # noqa: BLE001
            self.message_user(request, f"خطا: {exc!r}", messages.ERROR)


@admin.register(PricingFormula)
class PricingFormulaAdmin(admin.ModelAdmin):
    list_display = ("key", "value", "updated_by", "updated_at")
    search_fields = ("key", "description")
    list_per_page = 100

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
        emit_event(
            "pricing.formula.updated",
            actor={"type": "admin", "id": str(request.user.id)},
            target={"type": "pricing_formula", "id": obj.key},
            data={"value": str(obj.value)},
        )


@admin.register(PriceQuote)
class PriceQuoteAdmin(admin.ModelAdmin):
    list_display = ("quote_id", "user", "asset", "side",
                    "price_per_mg_rial", "valid_until", "created_at")
    list_filter = ("asset", "side")
    search_fields = ("user__phone",)
    date_hierarchy = "created_at"
    readonly_fields = tuple(f.name for f in PriceQuote._meta.fields)

    def has_add_permission(self, request) -> bool:
        return False
