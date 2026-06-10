from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from django_tinyuser import settings


class IsInvitor(BasePermission):
    """
    Permission class to check if the user can invite others.
    """

    def has_permission(self, request, view):
        """
        Return `True` if the user can invite others, `False` otherwise.

        Only staff and superusers can always invite others.

        Authenticated users can invite others if `INVITE_ALLOW_ALL_AUTHENTICATED_USERS` is `True` or they
        are in `INVITE_GROUPS`.

        :param request: The request object.
        :param view: The view object.
        :return: `True` if the user can invite others, `False` otherwise.
        """
        if request.user.is_authenticated:
            if request.user.is_staff:
                return True
            elif request.user.is_superuser:
                return True
            elif request.user.is_active:
                if settings.INVITE_ALLOW_ALL_AUTHENTICATED_USERS:
                    return True
                elif (
                    settings.INVITE_GROUPS
                    and request.user.groups.filter(
                        name__in=settings.INVITE_GROUPS
                    ).exists()
                ):
                    return True

            raise PermissionDenied()
        return False
