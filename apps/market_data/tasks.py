import redis
from celery import shared_task

redis_client = redis.StrictRedis(host="redis", port=6379, db=0)


@shared_task
def update_asset_prices():
    """
    Background task to fetch real-time prices and update Redis cache.
    """

    print("Fetching prices from External API...")

    # Ejemplo de cómo la tarea llenará Redis
    # prices = CoinGeckoService.get_all_prices()
    # for symbol, price in prices.items():
    #     redis_client.set(f"price_{symbol}", price)

    return "Prices updated successfully"
