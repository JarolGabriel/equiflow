from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import GitHubLogin, GoogleLogin, RegisterView, UserProfileView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("google/", GoogleLogin.as_view(), name="google_login"),
    path("github/", GitHubLogin.as_view(), name="github_login"),
]
