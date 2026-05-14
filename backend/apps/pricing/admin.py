from django.contrib import admin

from apps.audit.emit import emit_event

from .models import PriceQuote, PriceTick, PricingFormula


@admin.register(PriceTick)
class PriceTickAdmin(admin.ModelAdmin):
    list_display = ("source_key", "rial_price", "captured_at", "source")
    list_filter = ("source_key", "source")
    date_hierarchy = "captured_at"


@admin.register(PricingFormula)
class PricingFormulaAdmin(admin.ModelAdmin):
    list_display = ("key", "value", "updated_by", "updated_at")
    search_fields = ("key",)

    def save_model(self, request, obj, form, change):  # type: ignore[no-untyped-def]
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
    list_display = ("quote_id", "user", "asset", "side", "price_per_mg_rial", "valid_until")
    list_filter = ("asset", "side")
