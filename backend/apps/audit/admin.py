from django.contrib import admin

from .models import AuditEntry, IdempotencyKey


@admin.register(AuditEntry)
class AuditEntryAdmin(admin.ModelAdmin):
    list_display = ("kind", "category", "actor_id", "target_type", "target_id", "outcome", "created_at")
    list_filter = ("category", "outcome", "severity")
    search_fields = ("kind", "actor_id", "target_id", "request_id", "trace_id")
    readonly_fields = tuple(f.name for f in AuditEntry._meta.fields)


@admin.register(IdempotencyKey)
class IdempotencyKeyAdmin(admin.ModelAdmin):
    list_display = ("scope", "key", "created_at")
    search_fields = ("scope", "key")
