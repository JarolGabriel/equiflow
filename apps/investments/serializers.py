from rest_framework import serializers

from .models import Asset, Portfolio, PortfolioAsset


class AssetSerializer(serializers.ModelSerializer):
    """
    Serializer for the Asset model.
    Handles the global list of financial instruments.
    """

    class Meta:
        model = Asset
        fields = ["id", "symbol", "name", "asset_type", "exchange"]


class PortfolioAssetSerializer(serializers.ModelSerializer):
    """
    Serializer for the relationship between Portfolios and Assets.
    Includes nested asset details for better frontend readability.
    """

    asset_details = AssetSerializer(source="asset", read_only=True)

    class Meta:
        model = PortfolioAsset
        fields = [
            "id",
            "asset",
            "asset_details",
            "quantity",
            "average_purchase_price",
            "last_updated",
        ]


class PortfolioSerializer(serializers.ModelSerializer):
    """
    Main serializer for the Portfolio model.
    Includes the owner's email and the list of assets contained.
    """

    user_email = serializers.ReadOnlyField(source="user.email")

    assets = PortfolioAssetSerializer(many=True, read_only=True)

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
            "assets",
            "items",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):

        items_data = validated_data.pop("items", [])
        portfolio = Portfolio.objects.create(**validated_data)

        for item in items_data:
            PortfolioAsset.objects.create(
                portfolio=portfolio,
                asset_id=item["asset_id"],
                quantity=item["quantity"],
                average_purchase_price=item["price"],
            )
        return portfolio
