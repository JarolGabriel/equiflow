import requests

# from django.conf import settings


class CoinGeckoService:
    BASE_URL = "https://api.coingecko.com/api/v3"

    @staticmethod
    def get_prices(coin_ids=["bitcoin", "ethereum"]):

        url = f"{CoinGeckoService.BASE_URL}/simple/price"
        ids_query = ",".join(coin_ids)
        params = {"ids": ids_query, "vs_currencies": "usd"}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error en CoinGecko Multi-Price: {e}")
            return {}
