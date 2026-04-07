import logging

import redis
from celery import shared_task
from django.utils import timezone

from apps.alerts.services import AlertService
from apps.investments.models import Asset, AssetPriceHistory

from .services import CoinGeckoService, ForexService, StockService

logger = logging.getLogger(__name__)
redis_client = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)


@shared_task
def update_all_market_prices():
    """
    Optimized Celery task to synchronize prices into Redis.
    Uses Batch Requests for Cryptos, Stocks, and Forex.
    """
    assets_to_update = Asset.objects.all()
    summary = []

    # --- 1. CRYPTOCURRENCIES (COINGECKO) ---
    crypto_assets = assets_to_update.filter(asset_type="crypto").exclude(
        provider_id__isnull=True
    )
    if crypto_assets.exists():
        mapping = {a.provider_id: a.symbol for a in crypto_assets}
        prices_data = CoinGeckoService.get_prices(list(mapping.keys()))

        if prices_data:
            count = 0
            for cg_id, price_info in prices_data.items():
                symbol = mapping.get(cg_id)
                price = price_info.get("usd")
                change = price_info.get("usd_24h_change")

                if price is not None:
                    redis_client.set(f"price_{symbol}", str(price))
                    asset_obj = crypto_assets.filter(provider_id=cg_id).first()
                    if asset_obj:
                        AssetPriceHistory.objects.create(asset=asset_obj, price=price)
                    if change is not None:
                        redis_client.set(f"change_{symbol}", str(change))

                    AlertService.evaluate_alerts(symbol, float(price))
                    count += 1
            summary.append(f"Cryptos: {count} updated")

    # --- 2. STOCKS (TWELVE DATA - LIMITED TO 8 FOR FREE TIER) ---
    # We take only 8 to avoid credit exhaustion (8 credits/min limit)
    stock_assets = assets_to_update.filter(asset_type="stock")[:8]
    if stock_assets.exists():
        stock_symbols = [a.symbol.upper() for a in stock_assets]
        logger.info(f"Processing stocks (Batch of 8): {stock_symbols}")

        stock_data = StockService.get_stock_prices(stock_symbols)

        if stock_data and isinstance(stock_data, dict):
            count = 0
            for asset in stock_assets:
                symbol_upper = asset.symbol.upper()
                asset_info = stock_data.get(symbol_upper)

                if isinstance(asset_info, dict) and (
                    asset_info.get("price") or asset_info.get("close")
                ):
                    price = asset_info.get("price") or asset_info.get("close")
                    if price:
                        redis_client.set(f"price_{asset.symbol}", str(price))
                        AssetPriceHistory.objects.create(asset=asset, price=price)
                        count += 1
            summary.append(f"Stocks: {count} updated")
        else:
            summary.append("Stocks: Failed (API Limit/Error)")

    # --- 3. FOREX (ALPHA VANTAGE) ---
    forex_assets = assets_to_update.filter(asset_type="forex")
    if forex_assets.exists():
        forex_symbols = [a.symbol.upper() for a in forex_assets]
        forex_data = ForexService.get_prices(forex_symbols)

        if forex_data and isinstance(forex_data, dict):
            count = 0
            for asset in forex_assets:
                symbol_upper = asset.symbol.upper()
                asset_info = forex_data.get(symbol_upper)

                if isinstance(asset_info, dict) and (
                    asset_info.get("price") or asset_info.get("close")
                ):
                    price = asset_info.get("price") or asset_info.get("close")
                    change = asset_info.get("percent_change", 0.0)

                    if price:
                        redis_client.set(f"price_{asset.symbol}", str(price))
                        AssetPriceHistory.objects.create(asset=asset, price=price)
                        redis_client.set(f"change_{asset.symbol}", str(change))
                        AlertService.evaluate_alerts(asset.symbol, float(price))
                        count += 1
            summary.append(f"Forex: {count} updated")
        else:
            summary.append("Forex: 0 updated (API Limit/Error)")

    # --- 4. TIMESTAMP ---
    last_update = timezone.now().isoformat()
    redis_client.set("market_last_updated", last_update)

    return " | ".join(summary)
