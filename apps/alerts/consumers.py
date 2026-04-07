import json

from channels.generic.websocket import AsyncWebsocketConsumer


class AlertConsumer(AsyncWebsocketConsumer):
    """
    Consumer to handle real-time price alert notifications.
    """

    async def connect(self):

        self.user = self.scope["user"]

        # If the user is not authenticated, we close the connection
        if self.user.is_anonymous:
            await self.close()
        else:
            # Each user has their own private group based on their ID
            self.group_name = f"user_alerts_{self.user.id}"

            # Join the group
            await self.channel_layer.group_add(self.group_name, self.channel_name)

            await self.accept()
            print(
                f"WebSocket connected: User {self.user.id} joined group {self.group_name}"
            )

    async def disconnect(self, close_code):
        # Leave the group when disconnecting
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            print(f"WebSocket disconnected: User {self.user.id}")

    # This method receives the message from the Channel Layer (sent by Celery/Service)
    async def send_alert_notification(self, event):
        """
        Custom handler to send the alert data to the actual WebSocket client.
        """
        payload = event["payload"]

        await self.send(text_data=json.dumps(payload))
