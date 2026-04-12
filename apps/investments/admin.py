from django.contrib import admin

from .models import Asset, AssetPriceHistory, Portfolio, PortfolioAsset, Transaction


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("symbol", "name", "asset_type", "exchange", "created_at")
    search_fields = ("symbol", "name")
    list_filter = ("asset_type", "exchange")
    ordering = ("symbol",)


class PortfolioAssetInline(admin.TabularInline):
    model = PortfolioAsset
    extra = 1
    autocomplete_fields = ["asset"]


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "currency",
        "is_public",
        "get_balance",
        "created_at",
    )
    search_fields = ("name", "user__email")
    list_filter = ("currency", "is_public")
    inlines = [PortfolioAssetInline]

    def get_balance(self, obj):
        return f"{obj.total_balance:.2f} {obj.currency}"

    get_balance.short_description = "Total Balance"


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "portfolio",
        "asset",
        "transaction_type",
        "quantity",
        "price_at_transaction",
    )
    list_filter = ("transaction_type", "created_at")
    search_fields = ("asset__symbol", "portfolio__name")
    date_hierarchy = "created_at"


@admin.register(AssetPriceHistory)
class AssetPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ("asset", "price", "timestamp")
    list_filter = ("asset", "timestamp")
    readonly_fields = ("timestamp",)
