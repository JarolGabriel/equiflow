from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AssetViewSet, GlobalMarketStatusAPIView

router = DefaultRouter()
router.register(r"assets", AssetViewSet, basename="asset")

urlpatterns = [
    path("status/", GlobalMarketStatusAPIView.as_view(), name="market-global-status"),
    path("", include(router.urls)),
]
