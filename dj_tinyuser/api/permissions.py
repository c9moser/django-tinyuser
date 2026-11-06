"""Permissions for WebAPI."""

from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from dj_tinyuser import settings


class IsInvitor(BasePermission):
    """Permission: is_invitor."""

    def has_permission(self, request, view):
        """Check for invitor permission."""
        if not request.user.is_authenticated:
            raise PermissionDenied("Not authenticated")

        if request.user.is_staff or bool(
            request.user.groups.filter(
                name__in=settings.INVITE_GROUPS if settings.INVITE_GROUPS else ["invitors"]
            ).first()
        ):
            return True

        raise PermissionDenied("Not an invitor.")
