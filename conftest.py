import pytest
from rest_framework.test import APIClient

from apps.investments.models import Asset, Portfolio


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        email="test@equiflow.com", password="password123"
    )


@pytest.fixture
def asset():
    return Asset.objects.create(symbol="BTC", name="Bitcoin", asset_type="crypto")


@pytest.fixture
def portfolio(user):
    return Portfolio.objects.create(user=user, name="My Main Portfolio")
