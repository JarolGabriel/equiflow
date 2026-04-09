import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import PriceAlert


class AlertService:
    @staticmethod
    def evaluate_alerts(asset_symbol, current_price):
        alerts = PriceAlert.objects.filter(
            asset__symbol=asset_symbol, status=PriceAlert.AlertStatus.PENDING
        ).select_related("user", "asset")

        channel_layer = get_channel_layer()

        for alert in alerts:
            is_triggered = False

            if alert.condition == PriceAlert.AlertCondition.ABOVE:
                if Decimal(str(current_price)) >= alert.target_price:
                    is_triggered = True
            elif alert.condition == PriceAlert.AlertCondition.BELOW:
                if Decimal(str(current_price)) <= alert.target_price:
                    is_triggered = True

            if is_triggered:
                alert.status = PriceAlert.AlertStatus.FIRED
                alert.save()

                group_name = f"user_alerts_{alert.user.id}"
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        "type": "send_alert_notification",
                        "payload": {
                            "message": f"¡Alerta! {alert.asset.symbol} ha llegado a {current_price}",
                            "asset": alert.asset.symbol,
                            "price": str(current_price),
                            "condition": alert.condition,
                        },
                    },
                )
                logger.info(
                    f"Alert notification dispatched to group: {group_name} for asset: {alert.asset.symbol}"
                )

        return alerts
