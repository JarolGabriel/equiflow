from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.permissions import AllowAny

from .models import Asset, Portfolio
from .serializers import AssetSerializer, PortfolioSerializer


class AssetViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing assets.
    Standard users can only list and retrieve assets, not create or delete them.
    """

    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [AllowAny]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["asset_type", "exchange"]

    search_fields = ["symbol", "name"]

    ordering_fields = ["symbol", "name", "created_at"]


class PortfolioViewSet(viewsets.ModelViewSet):
    """
    Main ViewSet for Portfolio management.
    Includes logic to ensure users only access their own data.
    """

    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Customizes the queryset to return only portfolios belonging to the current user.
        This is a critical security best practice.
        """
        return Portfolio.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Automatically assigns the logged-in user as the owner of the new portfolio.
        """
        serializer.save(user=self.request.user)
