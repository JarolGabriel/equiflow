from django.urls import path

from .views import GlobalMarketStatusAPIView

urlpatterns = [
    path("status/", GlobalMarketStatusAPIView.as_view(), name="market-global-status"),
]
