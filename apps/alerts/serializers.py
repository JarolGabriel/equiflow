from rest_framework import serializers

from .models import PriceAlert


class PriceAlertSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    asset_symbol = serializers.CharField(source="asset.symbol", read_only=True)

    class Meta:
        model = PriceAlert
        fields = [
            "id",
            "user_email",
            "asset",
            "asset_symbol",
            "target_price",
            "condition",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]

    def create(self, validated_data):

        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
