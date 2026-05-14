from django.contrib import admin

from .models import JewelryCategory


@admin.register(JewelryCategory)
class JewelryCategoryAdmin(admin.ModelAdmin):
    list_display = ("title_fa", "code", "parent", "sort")
