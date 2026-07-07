from rest_framework import serializers

from core.redis_utils import build_price_map, get_change, get_price

from .models import (
    Asset,
    AssetPriceHistory,
    FavoriteAsset,
    Portfolio,
    PortfolioAsset,
    Transaction,
)


def _merge_price_map(context, symbols):
    """Ensure ``context['price_map']`` covers ``symbols`` using a single batch
    call for the symbols that are not already cached in the context."""
    existing = context.get("price_map")
    if existing is None:
        existing = {}
    missing = [s for s in symbols if s not in existing]
    if missing:
        existing = {**existing, **build_price_map(missing)}
    context["price_map"] = existing
    return existing


class AssetListSerializer(serializers.ListSerializer):
    """Batches all Redis lookups for a list of assets into one MGET."""

    def to_representation(self, data):
        iterable = list(data.all()) if hasattr(data, "all") else list(data)
        _merge_price_map(self.child.context, [obj.symbol for obj in iterable])
        return [self.child.to_representation(item) for item in iterable]


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
        list_serializer_class = AssetListSerializer

    def _entry(self, symbol):
        price_map = self.context.get("price_map")
        if price_map is not None and symbol in price_map:
            return price_map[symbol]
        return None

    def get_price(self, obj):
        entry = self._entry(obj.symbol)
        return entry["price"] if entry is not None else get_price(obj.symbol)

    def get_change(self, obj):
        entry = self._entry(obj.symbol)
        return entry["change"] if entry is not None else get_change(obj.symbol)


class PortfolioAssetListSerializer(serializers.ListSerializer):
    """Batches all Redis lookups for a list of portfolio holdings into one MGET."""

    def to_representation(self, data):
        iterable = list(data.all()) if hasattr(data, "all") else list(data)
        _merge_price_map(self.child.context, [pa.asset.symbol for pa in iterable])
        return [self.child.to_representation(item) for item in iterable]


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
        list_serializer_class = PortfolioAssetListSerializer

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

    def _price(self, symbol):
        price_map = self.context.get("price_map")
        if price_map is not None and symbol in price_map:
            return price_map[symbol]["price"]
        return get_price(symbol)

    def get_current_balance(self, obj):
        price = self._price(obj.asset.symbol)
        if price is not None:
            return float(obj.quantity) * price
        return float(obj.quantity) * float(obj.average_purchase_price)

    def get_profit_loss(self, obj):
        price = self._price(obj.asset.symbol)
        if price is not None:
            current_val = float(obj.quantity) * price
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

    def to_representation(self, instance):
        # Prefetch every price this portfolio needs in a single Redis round trip
        # so the nested serializers and the totals below reuse the same map.
        _merge_price_map(
            self.context, [pa.asset.symbol for pa in instance.assets.all()]
        )
        return super().to_representation(instance)

    def _price(self, symbol):
        price_map = self.context.get("price_map")
        if price_map is not None and symbol in price_map:
            return price_map[symbol]["price"]
        return get_price(symbol)

    def get_total_balance(self, obj):
        total = 0.0
        for asset in obj.assets.all():
            price = self._price(asset.asset.symbol)
            current_price = (
                price if price is not None else float(asset.average_purchase_price)
            )
            total += float(asset.quantity) * current_price
        return total

    def get_total_profit_loss(self, obj):
        total_pl = 0.0
        for asset in obj.assets.all():
            price = self._price(asset.asset.symbol)
            if price is not None:
                current_val = float(asset.quantity) * price
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
