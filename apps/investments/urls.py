from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AssetViewSet, PortfolioViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"assets", AssetViewSet, basename="asset")
router.register(r"portfolios", PortfolioViewSet, basename="portfolio")


urlpatterns = [
    path("", include(router.urls)),
]
