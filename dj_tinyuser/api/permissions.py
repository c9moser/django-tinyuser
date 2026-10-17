"""Permissions for WebAPI."""

from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


class IsInvitor(BasePermission):
    """Permission: is_invitor."""

    def has_permission(self, request, view):
        """Check for invitor permission."""
        if not request.user.is_authenticated or not (
            request.user.is_staff or bool(request.user.groups.filter(name="invitors").first())
        ):
            raise PermissionDenied("Not an invitor.")

        return True
