from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .models import PriceAlert
from .serializers import PriceAlertSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List all my price alerts",
        description="Returns a list of alerts. Free users: limited to 3 active. PRO: unlimited.",
    ),
    create=extend_schema(
        summary="Create a new price alert",
        description="Create an alert. Free users are limited to 3 active (PENDING/PAUSED) alerts.",
    ),
    retrieve=extend_schema(summary="Get alert details"),
    update=extend_schema(summary="Update an alert"),
    destroy=extend_schema(summary="Delete an alert"),
)
class PriceAlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing price alerts.
    IMPORTANT: This feature is only available for PRO subscribers.
    """

    serializer_class = PriceAlertSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PriceAlert.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user

        if not user.is_pro:
            active_alerts_count = PriceAlert.objects.filter(
                user=user, status__in=["PENDING", "PAUSED"]
            ).count()

            if active_alerts_count >= 3:
                raise PermissionDenied(
                    {
                        "error": "Limit reached",
                        "message": "Free users are limited to 3 active alerts. Upgrade to PRO for unlimited access.",
                    }
                )

        serializer.save(user=user)
