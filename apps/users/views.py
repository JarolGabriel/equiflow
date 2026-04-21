import os

from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import UserProfileSerializer, UserRegisterSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer

    @extend_schema(
        summary="Register a new user",
        description="Creates a new user account in EquiFlow. After registration, the user must login to obtain a JWT token.",
        responses={201: UserRegisterSerializer},
        auth=[],
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "user": {
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
                "message": "User created successfully. Please login to get your token.",
            },
            status=status.HTTP_201_CREATED,
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    get:
    Retrieve the authenticated user's profile information.

    patch:
    Update specific fields of the user's profile.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    @extend_schema(
        summary="Get user profile",
        description="Returns the profile data of the currently logged-in user based on the JWT token.",
        responses={200: UserProfileSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update user profile",
        description="Updates profile details such as first_name, last_name, and profile_picture.",
        responses={200: UserProfileSerializer},
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_object(self):
        """
        Overrides get_object to return the current authenticated user.
        This eliminates the need for an /id/ in the URL.
        """
        return self.request.user


class GoogleLogin(SocialLoginView):
    """
    Google OAuth2 Login
    Receives an 'access_token' or 'code' from Google and returns a JWT.
    """

    adapter_class = GoogleOAuth2Adapter
    callback_url = os.getenv(
        "GOOGLE_CALLBACK_URL", "http://localhost:8000/api/users/google/callback/"
    )
    client_class = OAuth2Client


class GitHubLogin(SocialLoginView):
    """
    GitHub OAuth2 Login
    Receives a 'code' from GitHub and returns a JWT.
    """

    adapter_class = GitHubOAuth2Adapter
    callback_url = os.getenv(
        "GITHUB_CALLBACK_URL", "http://localhost:8000/api/users/github/callback/"
    )
    client_class = OAuth2Client
