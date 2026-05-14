"""Customise the Django admin site (branding + dashboard tweaks)."""
from __future__ import annotations

from django.contrib import admin


admin.site.site_header = "پنل مدیریت KeyhanGold"
admin.site.site_title = "KeyhanGold Admin"
admin.site.index_title = "خانه"
