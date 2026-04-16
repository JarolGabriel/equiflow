import redis
from django.conf import settings
from rest_framework import serializers

from .models import (
    Asset,
    AssetPriceHistory,
    FavoriteAsset,
    Portfolio,
    PortfolioAsset,
    Transaction,
)

redis_client = redis.from_url(settings.REDIS_URL)


class AssetSerializer(serializers.ModelSerializer):
    """
    Serializer for the Asset model.
    Handles the global list of financial instruments.
    """

    price = serializers.SerializerMethodField()
    change = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = ["id", "symbol", "name", "asset_type", "exchange", "price", "change"]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self._market_data_cache = {}

    def _fetch_all_prices(self, symbols):
        """
        Fetches all prices and changes in a single Redis batch request.
        """
        price_keys = [f"price_{s.upper()}" for s in symbols]
        change_keys = [f"change_{s.upper()}" for s in symbols]

        # MGET returns a list of values in one single network trip
        values = redis_client.mget(price_keys + change_keys)

        # Split results back into prices and changes
        mid = len(symbols)
        prices = values[:mid]
        changes = values[mid:]

        return {
            symbol: {"price": float(p) if p else None, "change": float(c) if c else 0.0}
            for symbol, p, c in zip(symbols, prices, changes)
        }

    def get_price(self, obj):

        price = redis_client.get(f"price_{obj.symbol}")
        return float(price) if price else None

    def get_change(self, obj):

        change_val = redis_client.get(f"change_{obj.symbol}")
        return float(change_val) if change_val else 0.0


class PortfolioAssetSerializer(serializers.ModelSerializer):
    """
    Serializer for the relationship between Portfolios and Assets.
    Includes nested asset details for better frontend readability.
    """

    asset_details = AssetSerializer(source="asset", read_only=True)

    current_balance = serializers.SerializerMethodField()
    profit_loss = serializers.SerializerMethodField()

    class Meta:
        model = PortfolioAsset
        fields = [
            "id",
            "asset",
            "asset_details",
            "quantity",
            "average_purchase_price",
            "current_balance",
            "profit_loss",
            "last_updated",
        ]

    def validate_quantity(self, value):

        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a cero.")
        return value

    def validate_average_purchase_price(self, value):

        if value <= 0:
            raise serializers.ValidationError(
                "El precio de compra debe ser un valor positivo."
            )
        return value

    def get_current_balance(self, obj):

        price = redis_client.get(f"price_{obj.asset.symbol}")
        if price:
            return float(obj.quantity) * float(price)
        return float(obj.quantity) * float(obj.average_purchase_price)

    def get_profit_loss(self, obj):
        price = redis_client.get(f"price_{obj.asset.symbol}")
        if price:
            current_val = float(obj.quantity) * float(price)
            purchase_val = float(obj.quantity) * float(obj.average_purchase_price)
            return current_val - purchase_val
        return 0.0


class PortfolioSerializer(serializers.ModelSerializer):
    """
    Main serializer for the Portfolio model.
    Includes the owner's email and the list of assets contained.
    """

    user_email = serializers.ReadOnlyField(source="user.email")

    assets = PortfolioAssetSerializer(many=True, read_only=True)

    total_balance = serializers.SerializerMethodField()
    total_profit_loss = serializers.SerializerMethodField()

    items = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=False
    )

    class Meta:
        model = Portfolio
        fields = [
            "id",
            "user_email",
            "name",
            "description",
            "currency",
            "is_public",
            "total_balance",
            "total_profit_loss",
            "assets",
            "items",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        """
        Creates a Portfolio and optionally initializes assets via transactions
        to ensure the Signal handles the math correctly.
        """
        items_data = validated_data.pop("items", [])
        portfolio = Portfolio.objects.create(**validated_data)

        for item in items_data:
            # We create a Transaction instead of a PortfolioAsset directly.
            # This triggers the Signal we just made!
            Transaction.objects.create(
                portfolio=portfolio,
                asset_id=item["asset_id"],
                quantity=item["quantity"],
                price_at_transaction=item["price"],
                transaction_type=Transaction.TransactionType.BUY,
            )
        return portfolio

    def get_total_balance(self, obj):

        total = 0
        for asset in obj.assets.all():
            price = redis_client.get(f"price_{asset.asset.symbol}")
            current_price = (
                float(price) if price else float(asset.average_purchase_price)
            )
            total += float(asset.quantity) * current_price
        return total

    def get_total_profit_loss(self, obj):
        total_pl = 0
        for asset in obj.assets.all():
            price = redis_client.get(f"price_{asset.asset.symbol}")
            if price:
                current_val = float(asset.quantity) * float(price)
                purchase_val = float(asset.quantity) * float(
                    asset.average_purchase_price
                )
                total_pl += current_val - purchase_val
        return total_pl


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for recording new financial transactions.
    Includes validation to prevent selling more than the available balance.
    """

    asset_symbol = serializers.ReadOnlyField(source="asset.symbol")

    class Meta:
        model = Transaction
        fields = [
            "id",
            "portfolio",
            "asset",
            "asset_symbol",
            "transaction_type",
            "quantity",
            "price_at_transaction",
            "fees",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, data):
        """
        Object-level validation to check if a sale is possible.
        """
        if data["transaction_type"] == Transaction.TransactionType.SELL:
            portfolio_asset = PortfolioAsset.objects.filter(
                portfolio=data["portfolio"], asset=data["asset"]
            ).first()

            if not portfolio_asset or portfolio_asset.quantity < data["quantity"]:
                raise serializers.ValidationError(
                    {"quantity": "Insufficient balance to perform this sale."}
                )

        return data


class AssetPriceHistorySerializer(serializers.ModelSerializer):
    price = serializers.FloatField()

    class Meta:
        model = AssetPriceHistory
        fields = ["price", "timestamp"]


# apps/investments/serializers.py
class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteAsset
        fields = ["id", "asset", "created_at"]
