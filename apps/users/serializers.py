from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving and updating user profile information.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_pro",
            "is_verified",
            "profile_picture",
            "created_at",
        ]
        read_only_fields = ["id", "email", "is_pro", "is_verified", "created_at"]
