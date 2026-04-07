import time

import requests
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()


class CoinGeckoService:
    BASE_URL = "https://api.coingecko.com/api/v3"

    @staticmethod
    def get_top_coins(limit=100):
        """
        Fetches the top coins by market capitalization from CoinGecko.
        Used to seed the initial Asset catalog in the database.
        """
        url = f"{CoinGeckoService.BASE_URL}/coins/markets"
        params = {
            "vs_currency": "usd",
            "include_24hr_change": "true",
            "order": "market_cap_desc",
            "per_page": limit,
            "page": 1,
            "sparkline": False,
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching top coins: {e}")
            return []

    @staticmethod
    def get_prices(coin_ids):
        """
        Fetches current prices for a specific list of coin IDs.
        Example coin_ids: ['bitcoin', 'ethereum', 'binancecoin']
        """
        url = f"{CoinGeckoService.BASE_URL}/simple/price"
        params = {
            "ids": ",".join(coin_ids),
            "vs_currencies": "usd",
            "include_24hr_change": "true",
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching live prices: {e}")
            return None


class StockService:
    BASE_URL = "https://api.twelvedata.com/quote"
    API_KEY = getattr(settings, "TWELVE_DATA_API_KEY", "")

    @staticmethod
    def get_stock_prices(symbols):
        """
        Fetch prices for multiple symbols in a single batch request.
        Handles API error responses and malformed data.
        """
        if not symbols:
            return None

        params = {
            "symbol": ",".join(symbols),
            "apikey": StockService.API_KEY,
            "source": "docs",
        }

        try:
            response = requests.get(StockService.BASE_URL, params=params, timeout=10)
            data = response.json()

            # --- DEFENSIVE CHECK ---
            # Twelve Data returns 'status': 'error' if API Key is invalid or limit reached
            if isinstance(data, dict) and data.get("status") == "error":
                print(f"❌ Twelve Data API Error: {data.get('message')}")
                return None

            # Handle single symbol response vs batch response
            if len(symbols) == 1 and "symbol" in data:
                return {data["symbol"]: data}

            return data
        except Exception as e:
            print(f"❌ Connection Error in StockService: {e}")
            return None


class ForexService:
    BASE_URL = "https://www.alphavantage.co/query"
    API_KEY = settings.ALPHA_VANTAGE_API_KEY

    @staticmethod
    def get_prices(symbols):
        """
        Fetches Forex prices from Alpha Vantage.
        Note: Alpha Vantage Free Tier is usually 5 calls per minute.
        """
        if not symbols:
            return None

        normalized = {}
        for index, symbol in enumerate(symbols):
            if index > 0:
                print(
                    f"Waiting 15s for next Forex pair ({symbol}) to respect Alpha Vantage limits..."
                )
                time.sleep(15)
            from_curr = symbol[:3]
            to_curr = symbol[3:]

            params = {
                "function": "CURRENCY_EXCHANGE_RATE",
                "from_currency": from_curr,
                "to_currency": to_curr,
                "apikey": ForexService.API_KEY,
            }

            try:
                response = requests.get(
                    ForexService.BASE_URL, params=params, timeout=10
                )
                data = response.json()

                rate_data = data.get("Realtime Currency Exchange Rate")
                if rate_data:
                    normalized[symbol] = {
                        "price": rate_data.get("5. Exchange Rate"),
                        "percent_change": 0.0,
                    }
                else:
                    print(
                        f"⚠️ Alpha Vantage Error for {symbol}: {data.get('Note', 'Unknown error')}"
                    )
            except Exception as e:
                print(f"❌ Connection Error Alpha Vantage: {e}")

        return normalized
