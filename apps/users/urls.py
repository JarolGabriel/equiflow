from dj_rest_auth.views import (
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    GitHubLogin,
    GoogleLogin,
    RegisterView,
    UserProfileView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("logout/", LogoutView.as_view(), name="rest_logout"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("google/", GoogleLogin.as_view(), name="google_login"),
    path("github/", GitHubLogin.as_view(), name="github_login"),
    path("password/reset/", PasswordResetView.as_view(), name="rest_password_reset"),
    path(
        "password/reset/confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="rest_password_reset_confirm",
    ),
    path("password/change/", PasswordChangeView.as_view(), name="rest_password_change"),
]
