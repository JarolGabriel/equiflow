import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models


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
        # Por ahora, simulamos que el precio actual es un 10% más que el de compra
        # Mañana esto vendrá de Redis
        current_market_price = self.average_purchase_price * Decimal("1.10")
        return self.quantity * current_market_price

    @property
    def profit_loss(self):
        """
        Calculates the net profit or loss for this position.
        """
        return self.current_value - (self.quantity * self.average_purchase_price)
