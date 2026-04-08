from rest_framework import permissions


class IsProUser(permissions.BasePermission):
    """
    Custom permission to only allow access to users with PRO status.
    """

    message = "This feature is exclusive to users with a PRO subscription."

    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.is_pro
