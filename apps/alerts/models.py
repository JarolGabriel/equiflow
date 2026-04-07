import uuid

from django.conf import settings
from django.db import models

from apps.investments.models import Asset


class PriceAlert(models.Model):
    """
    Represents a user-defined alert for an asset price.
    """

    # Using a Choice class for better readability and maintainability
    class AlertCondition(models.TextChoices):
        ABOVE = "ABOVE", "Price is above"
        BELOW = "BELOW", "Price is below"

    class AlertStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        FIRED = "FIRED", "Fired"
        PAUSED = "PAUSED", "Paused"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="price_alerts"
    )
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="alerts")
    target_price = models.DecimalField(max_digits=20, decimal_places=8)
    condition = models.CharField(
        max_length=10, choices=AlertCondition.choices, default=AlertCondition.ABOVE
    )
    status = models.CharField(
        max_length=10, choices=AlertStatus.choices, default=AlertStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.asset.symbol} {self.condition} {self.target_price}"
