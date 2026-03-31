from django.core.management.base import BaseCommand

from apps.investments.models import Asset
from apps.market_data.services import CoinGeckoService


class Command(BaseCommand):
    """
    Custom management command to populate the Asset table with
    top cryptocurrencies from CoinGecko API.
    """

    help = "Seeds the database with top financial assets"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Fetching data from CoinGecko..."))

        coins = CoinGeckoService.get_top_coins(limit=100)

        if not coins:
            self.stdout.write(self.style.ERROR("No coins found or API error."))
            return

        created_count = 0
        for coin in coins:
            asset, created = Asset.objects.get_or_create(
                symbol=coin["symbol"].upper(),
                defaults={
                    "name": coin["name"],
                    "asset_type": "crypto",
                    "exchange": "CoinGecko",
                },
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Successfully seeded {created_count} new assets!")
        )
