"""
Custom adapters for django-allauth social authentication.
Handles both registration and login scenarios for OAuth providers.
"""

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter to handle OAuth login/registration flow.

    Allows users to:
    - Register with OAuth if they don't exist (auto-signup)
    - Login with OAuth if they already exist (auto-connect)
    """

    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a social provider,
        but before the login is actually processed (and before the user is created/connected).

        This method connects an existing user account to the social account
        if the email already exists in the database.
        """

        if sociallogin.is_existing:
            return

        email = None
        if sociallogin.account.provider == "github":
            email = sociallogin.account.extra_data.get("email")
        elif sociallogin.account.provider == "google":
            email = sociallogin.account.extra_data.get("email")

        if not email:
            return

        try:
            user = User.objects.get(email=email)

            sociallogin.connect(request, user)

        except User.DoesNotExist:
            pass
