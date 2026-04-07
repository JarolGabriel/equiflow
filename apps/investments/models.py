import uuid

from django.conf import settings
from django.db import models

from .services import PriceService


class Asset(models.Model):
    """
    Represents a financial instrument (Stock, Crypto, Forex).
    Shared across all users to maintain data integrity.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    symbol = models.CharField(max_length=20, unique=True)  # Ej: BTC, AAPL
    name = models.CharField(max_length=100)
    asset_type = models.CharField(max_length=20)  # stock, crypto
    exchange = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.symbol} - {self.name}"

    provider_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="ID used by the price provider (e.g., 'bitcoin' for CoinGecko)",
    )


class Portfolio(models.Model):
    """
    A collection of assets owned by a specific user.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="portfolios"
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    currency = models.CharField(max_length=10, default="USD")
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.email})"

    @property
    def total_balance(self):

        return sum(item.current_value for item in self.assets.all())

    @property
    def total_profit_loss(self):

        return sum(item.profit_loss for item in self.assets.all())


class PortfolioAsset(models.Model):
    """
    Intermediate model to manage quantities of assets within a portfolio.
    Implements a Many-to-Many relationship with extra data.
    """

    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="assets"
    )
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    average_purchase_price = models.DecimalField(max_digits=20, decimal_places=8)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("portfolio", "asset")

    def __str__(self):
        return f"{self.quantity} of {self.asset.symbol} in {self.portfolio.name}"

    @property
    def current_value(self):
        """
        Calculates the total value of this asset position based on a market price.
        Formula: quantity * current_market_price
        """

        market_price = PriceService.get_current_price(self.asset.symbol)

        if market_price is None:
            market_price = self.average_purchase_price

        return self.quantity * market_price

    @property
    def profit_loss(self):
        """
        Calculates the net profit or loss for this position.
        """
        return self.current_value - (self.quantity * self.average_purchase_price)


class Transaction(models.Model):
    """
    Represents an individual buy or sell operation within a portfolio.
    This is the source of truth for all balance and P&L calculations.
    """

    class TransactionType(models.TextChoices):
        BUY = "BUY", "Buy"
        SELL = "SELL", "Sell"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="transactions",
        help_text="The portfolio where this transaction belongs.",
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.PROTECT,
        related_name="transactions",
        help_text="The financial instrument being traded.",
    )
    transaction_type = models.CharField(
        max_length=4, choices=TransactionType.choices, default=TransactionType.BUY
    )
    quantity = models.DecimalField(
        max_digits=20, decimal_places=8, help_text="Amount of the asset traded."
    )
    price_at_transaction = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        help_text="Price of the asset at the moment of the transaction.",
    )
    fees = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=0,
        help_text="Transaction fees if applicable.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp of when the transaction was recorded."
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.transaction_type} {self.quantity} {self.asset.symbol} - {self.portfolio.name}"


class AssetPriceHistory(models.Model):
    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name="price_history"
    )
    price = models.DecimalField(max_digits=20, decimal_places=8)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

        indexes = [
            models.Index(fields=["asset", "timestamp"]),
        ]
