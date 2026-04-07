from rest_framework import viewsets

from .models import PriceAlert
from .serializers import PriceAlertSerializer


class PriceAlertViewSet(viewsets.ModelViewSet):
    serializer_class = PriceAlertSerializer

    def get_queryset(self):

        return PriceAlert.objects.filter(user=self.request.user)
