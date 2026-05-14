from django.contrib import admin

from .models import PaymentAttempt


@admin.register(PaymentAttempt)
class PaymentAttemptAdmin(admin.ModelAdmin):
    list_display = ("order", "gateway", "state", "amount_rial", "ref_id", "created_at")
    list_filter = ("gateway", "state")
    search_fields = ("authority", "ref_id", "order__order_number")
    readonly_fields = ("raw_request", "raw_response", "created_at", "completed_at")
