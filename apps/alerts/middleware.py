from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from jwt import decode as jwt_decode
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken

User = get_user_model()


@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


class JWTAuthMiddleware:
    """
    Custom middleware to authenticate WebSockets using JWT in the query string.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Close old database connections to prevent memory leaks
        query_string = scope.get("query_string", b"").decode()
        token = None

        # We look for ?token=YOUR_JWT_HERE in the URL
        for param in query_string.split("&"):
            if param.startswith("token="):
                token = param.split("=")[1]

        if token:
            try:
                # Validate token
                UntypedToken(token)
                decoded_data = jwt_decode(
                    token, settings.SECRET_KEY, algorithms=["HS256"]
                )
                user_id = decoded_data["user_id"]
                scope["user"] = await get_user(user_id)
            except (InvalidToken, TokenError, KeyError):
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await self.app(scope, receive, send)
