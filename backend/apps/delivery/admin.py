from django.contrib import admin

from .models import DeliveryRequest


@admin.register(DeliveryRequest)
class DeliveryRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "asset", "requested_mg", "state", "tracking_code", "created_at")
    list_filter = ("state", "asset")
    search_fields = ("user__phone", "tracking_code", "recipient_national_id")
