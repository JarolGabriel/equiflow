import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

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
            logger.error(
                "Failed to fetch price from Redis for symbol %s: %s", asset_symbol, e
            )

        return None
