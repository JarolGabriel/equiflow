from datetime import datetime

from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend

# Importaciones para Swagger
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# from apps.users.permissions import IsProUser
from .models import Asset, FavoriteAsset, Portfolio, PortfolioAsset, Transaction
from .serializers import (
    AssetPriceHistorySerializer,
    AssetSerializer,
    FavoriteSerializer,
    PortfolioAssetSerializer,
    PortfolioSerializer,
    TransactionSerializer,
)
from .services import PortfolioReportService


@extend_schema_view(
    list=extend_schema(
        summary="List all available assets",
        description="Retrieve a list of stocks, cryptos, and forex pairs supported by EquiFlow.",
    ),
    retrieve=extend_schema(summary="Get asset details"),
)
class AssetViewSet(viewsets.ReadOnlyModelViewSet):
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

    @extend_schema(
        summary="Get asset price history",
        description="Returns the last 50 price points for a specific asset to build charts.",
    )
    @action(detail=True, methods=["get"], url_path="history")
    def get_price_history(self, request, pk=None):
        asset = self.get_object()
        history = asset.price_history.all()[:50]
        serializer = AssetPriceHistorySerializer(history, many=True)
        return Response({"symbol": asset.symbol, "history": serializer.data})


@extend_schema_view(
    list=extend_schema(
        summary="List user portfolios",
        description="Get all portfolios belonging to the authenticated user with total balance calculations.",
    ),
    create=extend_schema(
        summary="Create a new portfolio",
        description="Create a new portfolio. **Free users are limited to 3 portfolios.** Upgrade to PRO for unlimited access.",
    ),
    retrieve=extend_schema(summary="Get portfolio details"),
    update=extend_schema(summary="Full update of a portfolio"),
    partial_update=extend_schema(summary="Partial update of a portfolio"),
    destroy=extend_schema(summary="Delete a portfolio"),
)
class PortfolioViewSet(viewsets.ModelViewSet):
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user).prefetch_related(
            "assets__asset"
        )

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_pro:
            portfolio_count = Portfolio.objects.filter(user=user).count()
            if portfolio_count >= 3:
                from rest_framework.exceptions import PermissionDenied

                raise PermissionDenied(
                    {
                        "error": "Limit reached",
                        "message": "Free users can only create up to 3 portfolios. Upgrade to PRO for unlimited access.",
                    }
                )
        serializer.save(user=user)


@extend_schema_view(
    list=extend_schema(summary="List all transactions"),
    create=extend_schema(
        summary="Record a new transaction",
        description="Register a BUY or SELL operation. This updates the portfolio's asset quantities automatically.",
    ),
    retrieve=extend_schema(summary="Get transaction details"),
    destroy=extend_schema(summary="Delete a transaction record"),
)
class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(portfolio__user=self.request.user)

    def perform_create(self, serializer):
        portfolio = serializer.validated_data["portfolio"]
        if portfolio.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("You do not own this portfolio.")
        serializer.save()


class MarketSummaryAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Market Dashboard Summary",
        description="Returns grouped assets (crypto, stocks, forex) with their latest prices for the main dashboard.",
    )
    def get(self, request):
        assets = Asset.objects.all()
        serializer = AssetSerializer(assets, many=True)
        data = serializer.data
        summary = {
            "cryptos": [a for a in data if a["asset_type"] == "crypto"],
            "stocks": [a for a in data if a["asset_type"] == "stock"],
            "forex": [a for a in data if a["asset_type"] == "forex"],
        }
        return Response(summary)


@extend_schema_view(
    list=extend_schema(
        summary="List portfolio assets",
        description="Shows the current holdings (quantity and value) within the user's portfolios.",
    ),
    destroy=extend_schema(
        summary="Remove asset from portfolio",
        description="Deletes the position of an asset in a portfolio.",
    ),
)
class PortfolioAssetViewSet(
    mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    queryset = PortfolioAsset.objects.all()
    serializer_class = PortfolioAssetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PortfolioAsset.objects.filter(portfolio__user=self.request.user)


class ExportPortfolioPDFView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Export Portfolio to PDF",
        description="Generates a professional financial report. **Free users get 1 free download**, then requires PRO.",
        responses={200: bytes},
    )
    def get(self, request, portfolio_id):
        user = request.user
        if not user.is_pro:
            if user.pdf_downloads >= 1:
                return Response(
                    {
                        "detail": "This feature is exclusive to users with a PRO subscription. You have already used your free download."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        try:
            portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
        except Portfolio.DoesNotExist:
            return Response(
                {"error": "Portfolio not found."}, status=status.HTTP_404_NOT_FOUND
            )

        pdf_buffer = PortfolioReportService.generate_pdf(portfolio)

        if not user.is_pro:
            user.pdf_downloads += 1
            user.save()
        filename = (
            f"EquiFlow_Report_{portfolio.name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        )

        return FileResponse(
            pdf_buffer,
            as_attachment=True,
            filename=filename,
            content_type="application/pdf",
        )


# apps/investments/views.py
class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return FavoriteAsset.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
