from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PriceAlertViewSet

router = DefaultRouter()
router.register(r"my-alerts", PriceAlertViewSet, basename="pricealert")

urlpatterns = [
    path("", include(router.urls)),
]
