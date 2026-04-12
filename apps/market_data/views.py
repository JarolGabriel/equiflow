import redis
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.investments.models import Asset, FavoriteAsset
from apps.investments.serializers import AssetSerializer

redis_client = redis.StrictRedis(
    host=getattr(settings, "REDIS_HOST", "redis"),
    port=6379,
    db=0,
    decode_responses=True,
)


class GlobalMarketStatusAPIView(APIView):
    """
    Public endpoint to fetch real-time market data directly from Redis.
    This bypasses PostgreSQL for maximum performance during dashboard updates.
    """

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


# apps/market_data/views.py


class AssetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

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

    @action(detail=False, methods=["get"], url_path="my-favorites")
    def my_favorites(self, request):

        favorite_ids = FavoriteAsset.objects.filter(user=request.user).values_list(
            "asset_id", flat=True
        )

        favorites = Asset.objects.filter(id__in=favorite_ids)

        serializer = self.get_serializer(favorites, many=True)

        return Response(serializer.data)
