from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from apps.audit.emit import emit_event

from .models import KYCSubmission, OTPCode, User
from .services import kyc as kyc_svc


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("phone", "first_name", "last_name", "is_verified",
                    "is_phone_verified", "is_vendor", "is_frozen",
                    "tier", "two_factor_enabled", "created_at")
    list_filter = ("is_verified", "is_phone_verified", "is_vendor",
                   "is_frozen", "tier", "is_staff", "is_superuser")
    search_fields = ("phone", "email", "national_id_hash", "iban_hash",
                     "first_name", "last_name")
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at", "national_id_hash",
                       "iban_hash", "last_login", "date_joined" if False else "created_at")
    fieldsets = (
        ("هویت", {"fields": ("id", "phone", "email", "first_name", "last_name",
                              "father_name", "birth_date")}),
        ("کد ملی و شبا", {"fields": ("national_id", "national_id_hash",
                                       "iban", "iban_hash"),
                            "classes": ("collapse",)}),
        ("نشانی", {"fields": ("address", "postal_code")}),
        ("وضعیت", {"fields": ("is_active", "is_verified", "is_phone_verified",
                                "is_vendor", "is_frozen", "tier")}),
        ("امنیت", {"fields": ("two_factor_enabled", "share_trades")}),
        ("سیستم", {"fields": ("is_staff", "is_superuser", "groups",
                                "user_permissions", "last_login",
                                "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone", "password1", "password2"),
        }),
    )
    actions = ["action_freeze", "action_unfreeze"]

    @admin.action(description="مسدودسازی کاربران انتخاب‌شده")
    def action_freeze(self, request, queryset):
        n = queryset.update(is_frozen=True)
        for u in queryset:
            emit_event("accounts.user.frozen", severity="critical",
                       actor={"type": "admin", "id": str(request.user.id)},
                       target={"type": "user", "id": str(u.id)},
                       data={"reason": "bulk admin action"})
        self.message_user(request, f"{n} کاربر مسدود شد.", messages.WARNING)

    @admin.action(description="بازفعال کاربران انتخاب‌شده")
    def action_unfreeze(self, request, queryset):
        n = queryset.update(is_frozen=False)
        self.message_user(request, f"{n} کاربر بازفعال شد.", messages.SUCCESS)


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ("phone", "purpose", "used", "attempts", "expires_at", "created_at")
    list_filter = ("purpose", "used")
    search_fields = ("phone",)
    readonly_fields = tuple(f.name for f in OTPCode._meta.fields)

    def has_add_permission(self, request) -> bool:
        return False


@admin.register(KYCSubmission)
class KYCSubmissionAdmin(admin.ModelAdmin):
    list_display = ("user", "state_badge", "reviewed_by", "reviewed_at", "created_at")
    list_filter = ("state",)
    search_fields = ("user__phone", "user__first_name", "user__last_name")
    readonly_fields = ("id", "created_at", "updated_at", "reviewed_at", "reviewed_by")
    fieldsets = (
        ("کاربر", {"fields": ("id", "user", "state")}),
        ("مدارک", {"fields": ("national_card_front", "national_card_back",
                                "selfie_with_card", "birth_certificate",
                                "video_attestation", "card_pan_masked")}),
        ("بررسی", {"fields": ("rejection_reason", "reviewed_by", "reviewed_at")}),
        ("متادیتا", {"fields": ("metadata", "created_at", "updated_at"),
                       "classes": ("collapse",)}),
    )
    actions = ["action_approve", "action_reject", "action_request_more"]

    @admin.display(description="وضعیت")
    def state_badge(self, obj):
        colors = {"empty": "#9CA3AF", "submitted": "#2D87F0",
                  "under_review": "#7C5CFF", "approved": "#16A34A",
                  "rejected": "#DC2626", "requires_more": "#F59E0B"}
        c = colors.get(obj.state, "#000")
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px;font-size:11px">{}</span>',
            c, obj.get_state_display(),
        )

    @admin.action(description="تأیید")
    def action_approve(self, request, queryset):
        n = 0
        for sub in queryset:
            if sub.state == "submitted":
                kyc_svc.start_review(sub, reviewer=request.user)
            try:
                kyc_svc.approve(sub, reviewer=request.user)
                n += 1
            except Exception:  # noqa: BLE001
                pass
        self.message_user(request, f"{n} درخواست تأیید شد.", messages.SUCCESS)

    @admin.action(description="رد (با علت)")
    def action_reject(self, request, queryset):
        n = 0
        for sub in queryset:
            if sub.state == "submitted":
                kyc_svc.start_review(sub, reviewer=request.user)
            try:
                kyc_svc.reject(sub, reviewer=request.user, reason="bulk reject")
                n += 1
            except Exception:  # noqa: BLE001
                pass
        self.message_user(request, f"{n} درخواست رد شد.", messages.WARNING)

    @admin.action(description="نیاز به اطلاعات بیشتر")
    def action_request_more(self, request, queryset):
        from apps.audit.state_machine import kyc_sm

        n = 0
        for sub in queryset:
            try:
                if sub.state == "submitted":
                    kyc_sm.fire(sub, "kyc.start_review",
                                actor={"type": "admin", "id": str(request.user.id)})
                kyc_sm.fire(sub, "kyc.require_more",
                            actor={"type": "admin", "id": str(request.user.id)})
                n += 1
            except Exception:  # noqa: BLE001
                pass
        self.message_user(request, f"{n} درخواست به حالت 'نیاز به اطلاعات بیشتر' رفت.",
                          messages.INFO)
