from datetime import datetime

from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsProUser

from .models import Asset, Portfolio, PortfolioAsset, Transaction
from .serializers import (
    AssetPriceHistorySerializer,
    AssetSerializer,
    PortfolioAssetSerializer,
    PortfolioSerializer,
    TransactionSerializer,
)
from .services import PortfolioReportService


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

    @action(detail=True, methods=["get"], url_path="history")
    def get_price_history(self, request, pk=None):
        """
        Retorna los últimos 50 registros de precio para este activo específico.
        URL: /api/investments/assets/{id}/history/
        """
        asset = self.get_object()

        history = asset.price_history.all()[:50]
        serializer = AssetPriceHistorySerializer(history, many=True)
        return Response({"symbol": asset.symbol, "history": serializer.data})


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
        return Portfolio.objects.filter(user=self.request.user).prefetch_related(
            "assets__asset"
        )

    def perform_create(self, serializer):
        """
        Check for portfolio limits based on user status before saving.
        """
        user = self.request.user

        # 1. Lógica de Negocio: Usuarios gratuitos limitados a 3 portafolios
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


class TransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and creating financial transactions.
    Ensures that users can only interact with transactions
    from their own portfolios.
    """

    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter transactions to only show those belonging
        to the current user's portfolios.
        """
        return Transaction.objects.filter(portfolio__user=self.request.user)

    def perform_create(self, serializer):
        """
        Custom logic to ensure the portfolio belongs to the user
        before saving the transaction.
        """
        portfolio = serializer.validated_data["portfolio"]
        if portfolio.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("You do not own this portfolio.")

        serializer.save()


class MarketSummaryAPIView(APIView):
    """
    Vista personalizada para el Dashboard.
    Retorna activos agrupados por tipo con sus precios de Redis.
    """

    permission_classes = [AllowAny]

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


class PortfolioAssetViewSet(
    mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    """
    Allow list and delete specific Portfolio
    """

    queryset = PortfolioAsset.objects.all()
    serializer_class = PortfolioAssetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return PortfolioAsset.objects.filter(portfolio__user=self.request.user)


class ExportPortfolioPDFView(APIView):
    """
    API View to export a portfolio summary as a PDF file.
    Only available for PRO users.
    """

    permission_classes = [IsAuthenticated, IsProUser]

    def get(self, request, portfolio_id):
        try:
            # Ensure the user owns the portfolio they are trying to export
            portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
        except Portfolio.DoesNotExist:
            return Response({"error": "Portfolio not found."}, status=404)

        # Generate the PDF buffer
        pdf_buffer = PortfolioReportService.generate_pdf(portfolio)

        filename = (
            f"EquiFlow_Report_{portfolio.name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        )

        return FileResponse(
            pdf_buffer,
            as_attachment=True,
            filename=filename,
            content_type="application/pdf",
        )
