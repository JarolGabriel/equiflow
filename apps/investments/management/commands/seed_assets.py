from django.core.management.base import BaseCommand

from apps.investments.models import Asset
from apps.market_data.services import CoinGeckoService


class Command(BaseCommand):
    help = "Seeds the database with Cryptos, Stocks, and Forex assets"

    def handle(self, *args, **options):
        # 1. SEED CRYPTOS
        self.stdout.write(self.style.SUCCESS("--- Fetching Cryptos from CoinGecko ---"))
        coins = CoinGeckoService.get_top_coins(limit=100)
        if coins:
            for coin in coins:
                Asset.objects.update_or_create(
                    symbol=coin["symbol"].upper(),
                    defaults={
                        "name": coin["name"],
                        "asset_type": "crypto",
                        "exchange": "CoinGecko",
                        "provider_id": coin["id"],
                    },
                )
            self.stdout.write("✅ 100 Cryptos seeded.")

        # 2. SEED STOCKS
        self.stdout.write(self.style.SUCCESS("\n--- Seeding Top Stocks ---"))
        top_stocks = [
            ("AAPL", "Apple Inc."),
            ("MSFT", "Microsoft Corp."),
            ("GOOGL", "Alphabet Inc."),
            ("AMZN", "Amazon.com Inc."),
            ("TSLA", "Tesla Inc."),
            ("NVDA", "NVIDIA Corp."),
            ("META", "Meta Platforms Inc."),
            ("BRK.B", "Berkshire Hathaway"),
            ("V", "Visa Inc."),
            ("JPM", "JPMorgan Chase"),
            ("WMT", "Walmart Inc."),
            ("MA", "Mastercard Inc."),
            ("PG", "Procter & Gamble"),
            ("UNH", "UnitedHealth Group"),
            ("HD", "Home Depot"),
            ("BAC", "Bank of America"),
            ("DIS", "Walt Disney Co."),
            ("PFE", "Pfizer Inc."),
            ("NFLX", "Netflix Inc."),
            ("KO", "Coca-Cola Co."),
            ("PEP", "PepsiCo Inc."),
            ("COST", "Costco Wholesale"),
            ("ADBE", "Adobe Inc."),
            ("CRM", "Salesforce Inc."),
            ("AMD", "Advanced Micro Devices"),
        ]
        for symbol, name in top_stocks:
            Asset.objects.update_or_create(
                symbol=symbol,
                defaults={
                    "name": name,
                    "asset_type": "stock",
                    "exchange": "NASDAQ/NYSE",
                },
            )
        self.stdout.write(f"✅ {len(top_stocks)} Stocks seeded.")

        # 3. SEED FOREX
        self.stdout.write(self.style.SUCCESS("\n--- Seeding Forex Pairs ---"))
        forex_pairs = [
            ("EURUSD", "Euro / US Dollar"),
            ("GBPUSD", "British Pound / US Dollar"),
            ("JPYUSD", "Japanese Yen / US Dollar"),
            ("AUDUSD", "Australian Dollar / US Dollar"),
            ("CADUSD", "Canadian Dollar / US Dollar"),
        ]
        for symbol, name in forex_pairs:
            Asset.objects.update_or_create(
                symbol=symbol,
                defaults={
                    "name": name,
                    "asset_type": "forex",
                    "exchange": "Alpha Vantage",
                },
            )
        self.stdout.write(f"✅ {len(forex_pairs)} Forex pairs seeded.")

        self.stdout.write(self.style.SUCCESS("\n🚀 DATABASE FULLY SEEDED!"))
