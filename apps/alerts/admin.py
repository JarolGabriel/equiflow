from django.contrib import admin

from .models import PriceAlert


@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "asset",
        "target_price",
        "condition",
        "status",
        "created_at",
    )

    list_filter = ("status", "condition", "asset")

    search_fields = ("user__email", "asset__symbol")
