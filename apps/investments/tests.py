from decimal import Decimal

import pytest

from apps.investments.models import PortfolioAsset, Transaction


@pytest.mark.django_db
class TestInvestmentSignals:
    """
    Test suite to verify that signals correctly update portfolio data.
    """

    def test_transaction_updates_portfolio_asset_quantity(self, user, portfolio, asset):
        """
        Verify that creating a BUY transaction correctly updates
        the PortfolioAsset quantity and average price.
        """
        # 1. Setup: Define transaction data
        quantity = Decimal("2.0")
        price = Decimal("50000.0")

        # 2. Action: Create a transaction (This triggers the signal)
        Transaction.objects.create(
            portfolio=portfolio,
            asset=asset,
            transaction_type=Transaction.TransactionType.BUY,
            quantity=quantity,
            price_at_transaction=price,
        )

        # 3. Assertion: Check if PortfolioAsset was created and updated
        p_asset = PortfolioAsset.objects.get(portfolio=portfolio, asset=asset)

        assert p_asset.quantity == quantity
        assert p_asset.average_purchase_price == price

    def test_insufficient_balance_validation(self, api_client, user, portfolio, asset):
        """
        Ensure the serializer prevents selling more than what is available.
        """
        api_client.force_authenticate(user=user)

        # Action: Attempt to sell without having any balance
        url = "/api/investments/transactions/"
        data = {
            "portfolio": portfolio.id,
            "asset": asset.id,
            "transaction_type": "SELL",
            "quantity": 10.0,
            "price_at_transaction": 100.0,
        }

        response = api_client.post(url, data)

        # Assertion: Should fail with a 400 Bad Request
        assert response.status_code == 400
        assert "Insufficient balance" in str(response.data)


@pytest.mark.django_db
class TestPortfolioSecurity:
    """
    Test suite to ensure data privacy between different users.
    """

    def test_user_cannot_access_others_portfolio(
        self, api_client, django_user_model, portfolio
    ):
        """
        Verify that an authenticated user receives a 404 or empty list
        when trying to access a portfolio they do not own.
        """
        # 1. Setup: Create a second user (Hacker)
        hacker = django_user_model.objects.create_user(
            email="hacker@test.com", password="password123"
        )
        api_client.force_authenticate(user=hacker)

        # 2. Action: Try to access the first user's portfolio
        url = f"/api/investments/portfolios/{portfolio.id}/"
        response = api_client.get(url)

        # 3. Assertion: Should be 404 Not Found (Django Rest Framework's default for privacy)
        assert response.status_code == 404

    def test_user_can_only_list_their_own_portfolios(
        self, api_client, django_user_model, portfolio
    ):
        """
        Verify that the portfolio list only returns items owned by the requester.
        """
        # Create a second user with their own portfolio
        user2 = django_user_model.objects.create_user(
            email="user2@test.com", password="123"
        )
        from apps.investments.models import Portfolio

        Portfolio.objects.create(user=user2, name="User 2 Portfolio")

        # Authenticate as the first user
        api_client.force_authenticate(user=portfolio.user)

        # Action
        url = "/api/investments/portfolios/"
        response = api_client.get(url)

        # Assertion: Should only see 1 portfolio (theirs), not 2.
        assert len(response.data) == 1
        assert response.data[0]["name"] == portfolio.name
