from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PortfolioAsset, Transaction


@receiver(post_save, sender=Transaction)
def update_portfolio_asset_on_transaction(sender, instance, created, **kwargs):
    """
    Signal to update or create a PortfolioAsset whenever a Transaction is saved.
    It recalculates the total quantity and the weighted average purchase price.
    """
    if created:
        with transaction.atomic():
            portfolio_asset, _ = PortfolioAsset.objects.get_or_create(
                portfolio=instance.portfolio,
                asset=instance.asset,
                defaults={"quantity": 0, "average_purchase_price": 0},
            )

            if instance.transaction_type == Transaction.TransactionType.BUY:
                # Formula for Weighted Average Purchase Price
                total_cost = (
                    portfolio_asset.quantity * portfolio_asset.average_purchase_price
                ) + (instance.quantity * instance.price_at_transaction)

                new_quantity = portfolio_asset.quantity + instance.quantity

                if new_quantity > 0:
                    portfolio_asset.average_purchase_price = total_cost / new_quantity

                portfolio_asset.quantity = new_quantity

            elif instance.transaction_type == Transaction.TransactionType.SELL:
                # For sales, we only reduce quantity. Average purchase price remains the same.
                portfolio_asset.quantity -= instance.quantity

            portfolio_asset.save()
