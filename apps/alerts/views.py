from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.users.permissions import IsProUser

from .models import PriceAlert
from .serializers import PriceAlertSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List all my price alerts",
        description="Returns a list of all alerts created by the authenticated PRO user.",
    ),
    create=extend_schema(
        summary="Create a new price alert",
        description="Allows a PRO user to set a target price for an asset. Requires a valid Asset ID.",
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

    permission_classes = [IsAuthenticated, IsProUser]

    def get_queryset(self):
        return PriceAlert.objects.filter(user=self.request.user)

    def perform_create(self, serializer):

        serializer.save(user=self.request.user)
