from django.contrib import admin

from .models import KYCSubmission, OTPCode, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("phone", "first_name", "last_name", "is_verified", "is_vendor", "tier", "created_at")
    list_filter = ("is_verified", "is_phone_verified", "is_vendor", "is_frozen", "tier")
    search_fields = ("phone", "email", "national_id_hash")


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ("phone", "purpose", "used", "attempts", "expires_at", "created_at")
    list_filter = ("purpose", "used")
    search_fields = ("phone",)


@admin.register(KYCSubmission)
class KYCSubmissionAdmin(admin.ModelAdmin):
    list_display = ("user", "state", "reviewed_by", "reviewed_at", "created_at")
    list_filter = ("state",)
    search_fields = ("user__phone",)
