from django.contrib import admin

from .models import CoinType


@admin.register(CoinType)
class CoinTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "title_fa", "weight_mg", "gold_content_mg", "is_active")
