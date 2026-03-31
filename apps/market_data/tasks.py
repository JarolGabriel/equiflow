import redis
from celery import shared_task

from apps.investments.models import Asset

from .services import CoinGeckoService

redis_client = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)


@shared_task
def update_asset_prices():
    """
    Background task that synchronizes database assets with real-time
    market prices from CoinGecko and updates the Redis cache.
    """

    assets = Asset.objects.filter(asset_type="crypto")

    id_mapping = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "BNB": "binancecoin",
        "SOL": "solana",
    }

    active_ids = [id_mapping[a.symbol] for a in assets if a.symbol in id_mapping]

    if not active_ids:
        return "No active crypto assets to update."

    prices_data = CoinGeckoService.get_prices(active_ids)

    if prices_data:
        for symbol, cg_id in id_mapping.items():
            price = prices_data.get(cg_id, {}).get("usd")
            if price:
                redis_client.set(f"price_{symbol}", str(price))
                print(f"Celery: Updated {symbol} to ${price}")

        return f"Successfully updated {len(active_ids)} assets."

    return "Failed to fetch prices from CoinGecko."
