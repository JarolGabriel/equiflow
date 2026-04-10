from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_pro",
        "is_verified",
        "is_staff",
    )
    list_filter = ("is_pro", "is_verified", "is_staff", "is_superuser")

    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "profile_picture")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_pro",
                    "is_verified",
                )
            },
        ),
        (
            "Social & Security",
            {"fields": ("oauth_provider", "oauth_id", "two_factor_enabled")},
        ),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    readonly_fields = ("id", "created_at", "updated_at")

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password", "first_name", "last_name"),
            },
        ),
    )
    search_fields = ("email", "first_name", "last_name")
