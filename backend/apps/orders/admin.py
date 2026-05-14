from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "user", "kind", "state", "rial_amount", "mg_amount", "created_at")
    list_filter = ("kind", "state")
    search_fields = ("order_number", "user__phone", "payment_ref")
    inlines = [OrderItemInline]
    readonly_fields = ("created_at", "updated_at", "paid_at")
