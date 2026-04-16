import redis
from django.conf import settings
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.investments.models import Asset, FavoriteAsset
from apps.investments.serializers import AssetSerializer

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


class GlobalMarketStatusAPIView(APIView):
    """
    Public endpoint to fetch real-time market data directly from Redis.
    """

    @extend_schema(
        summary="Get Global Market Status (Real-time)",
        description="Fetches live asset prices and percentage changes directly from Redis cache.",
        responses={
            200: inline_serializer(
                name="MarketStatusResponse",
                fields={
                    "status": serializers.CharField(),
                    "last_update": serializers.CharField(),
                    "data": serializers.DictField(child=serializers.DictField()),
                },
            )
        },
    )
    def get(self, request, *args, **kwargs):
        try:
            price_keys = redis_client.keys("price_*")
            market_data = {}

            for key in price_keys:
                symbol = key.replace("price_", "")
                price = redis_client.get(key)
                change = redis_client.get(f"change_{symbol}")

                market_data[symbol] = {
                    "price": float(price) if price else None,
                    "change": float(change) if change is not None else None,
                }

            last_update = redis_client.get("market_last_updated")

            return Response(
                {
                    "status": "success",
                    "last_update": last_update,
                    "data": market_data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to fetch market data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AssetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

    @extend_schema(
        summary="Toggle Favorite Asset",
        description="Adds or removes an asset from the user's favorites list (Watchlist).",
        request=inline_serializer(
            name="ToggleFavoriteRequest", fields={"asset_id": serializers.UUIDField()}
        ),
        responses={
            200: inline_serializer(
                name="FavRemoved", fields={"status": serializers.CharField()}
            ),
            201: inline_serializer(
                name="FavAdded", fields={"status": serializers.CharField()}
            ),
        },
    )
    @action(detail=False, methods=["post"], url_path="toggle-favorite")
    def toggle_favorite(self, request):
        asset_id = request.data.get("asset_id")

        if not asset_id:
            return Response({"error": "asset_id is required"}, status=400)

        favorite, created = FavoriteAsset.objects.get_or_create(
            user=request.user, asset_id=asset_id
        )

        if not created:
            favorite.delete()
            return Response({"status": "removed"}, status=status.HTTP_200_OK)

        return Response({"status": "added"}, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="List My Favorites",
        description="Retrieves the detailed information of all assets marked as favorites by the authenticated user.",
        responses={200: AssetSerializer(many=True)},
        tags=["Favorites"],
    )
    @action(detail=False, methods=["get"], url_path="my-favorites")
    def my_favorites(self, request):
        favorite_ids = FavoriteAsset.objects.filter(user=request.user).values_list(
            "asset_id", flat=True
        )
        favorites = Asset.objects.filter(id__in=favorite_ids)
        serializer = self.get_serializer(favorites, many=True)
        return Response(serializer.data)
