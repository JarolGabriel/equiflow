import redis
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

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
