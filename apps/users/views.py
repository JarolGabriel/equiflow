from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import UserRegisterSerializer


class RegisterView(generics.CreateAPIView):
    """
    Endpoint for new user registration.
    Accessible by anyone (AllowAny).
    """

    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer

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
