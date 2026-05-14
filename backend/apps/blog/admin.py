from django.contrib import admin, messages
from django.utils import timezone
from django.utils.html import format_html

from .models import Category, Post, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title_fa", "code", "sort")
    search_fields = ("title_fa", "code")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("title_fa", "code")
    search_fields = ("title_fa", "code")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "state_badge", "category", "author", "views",
                    "published_at", "created_at")
    list_filter = ("state", "category", "tags")
    search_fields = ("title", "slug", "summary")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("category", "tags", "author")
    readonly_fields = ("id", "views", "created_at", "updated_at")
    fieldsets = (
        ("متن", {"fields": ("id", "title", "slug", "summary", "body_md", "cover_image")}),
        ("دسته‌بندی", {"fields": ("category", "tags")}),
        ("انتشار", {"fields": ("author", "state", "published_at")}),
        ("متادیتا", {"fields": ("views", "metadata", "created_at", "updated_at"),
                       "classes": ("collapse",)}),
    )
    actions = ["action_publish", "action_archive"]
    date_hierarchy = "published_at"

    @admin.display(description="وضعیت")
    def state_badge(self, obj):
        colors = {"draft": "#9CA3AF", "published": "#16A34A", "archived": "#6B7280"}
        c = colors.get(obj.state, "#000")
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px;font-size:11px">{}</span>',
            c, obj.get_state_display(),
        )

    @admin.action(description="انتشار پست‌های انتخاب‌شده")
    def action_publish(self, request, queryset):
        n = queryset.update(state="published", published_at=timezone.now())
        self.message_user(request, f"{n} پست منتشر شد.", messages.SUCCESS)

    @admin.action(description="بایگانی")
    def action_archive(self, request, queryset):
        n = queryset.update(state="archived")
        self.message_user(request, f"{n} پست بایگانی شد.", messages.INFO)
