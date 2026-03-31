import requests


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
