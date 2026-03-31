from decimal import Decimal

import redis

redis_client = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)


class PriceService:
    """
    Service layer to handle asset price retrieval from high-speed cache (Redis).
    """

    @staticmethod
    def get_current_price(asset_symbol):
        """
        Retrieves the latest price for a given asset symbol from Redis.

        Args:
            asset_symbol (str): The ticker symbol (e.g., 'BTC', 'ETH').

        Returns:
            Decimal: The current price if found in cache, None otherwise.
        """
        try:
            price = redis_client.get(f"price_{asset_symbol.upper()}")
            if price:
                return Decimal(price)
        except Exception as e:
            print(f"Redis error: {e}")

        return None
