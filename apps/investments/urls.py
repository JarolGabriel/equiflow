from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AssetViewSet,
    MarketSummaryAPIView,
    PortfolioAssetViewSet,
    PortfolioViewSet,
    TransactionViewSet,
)

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"assets", AssetViewSet, basename="asset")
router.register(r"portfolios", PortfolioViewSet, basename="portfolio")
router.register(r"transactions", TransactionViewSet, basename="transaction")
router.register(r"portfolio-assets", PortfolioAssetViewSet, basename="portfolio-asset")


urlpatterns = [
    path("", include(router.urls)),
    path("market-summary/", MarketSummaryAPIView.as_view(), name="market-summary"),
]
