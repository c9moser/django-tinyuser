from allauth.account.adapter import DefaultAccountAdapter
from django.forms import Form
from django.http import HttpRequest
from invitations.adapters import BaseInvitationsAdapter

from django_tinyuser import settings
from django_tinyuser.models import TinyUser


class TinyUserAccountAdapterBase:
    def save_user(
        self, request: HttpRequest, user: TinyUser, form: Form, commit: bool = True
    ):
        """
        Saves a new `User` instance using information provided in the signup form.

        :param request: The current HTTP request.
        :type request: HttpRequest
        :param user: User instance to be saved.
        :type user: TinyUser
        :param form: The signup form containing user data.
        :type form: forms.Form
        :param commit: Whether to commit the user to the database, defaults to True
        :type commit: bool, optional
        :return: The saved user instance.
        :rtype: TinyUser
        """
        from django.contrib.auth.models import Group

        # Only add to groups on user creation, not on update
        if user.pk is None:
            add_to_default_groups = True
        else:
            add_to_default_groups = False
        # Don't add to groups if we're not committing the user yet
        if not commit:
            add_to_default_groups = False

        user = super().save_user(request, user, form, commit)

        # Add the user to the default group if specified
        if add_to_default_groups:
            for group_name in settings.DEFAULT_USER_GROUPS:
                group, created = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)

        return user

    def allow_signup(self, request: HttpRequest) -> bool:
        """
        Determines whether signups are allowed based on the current request and settings.

        Logged in users are not allowed to sign up for new accounts,
        and the setting ALLOW_SIGNUP is checked for unauthenticated users.

        If ALLOW_SIGNUP is set to True, anyone can sign up.
        If it's set to False, signups are disabled and only invited users can sign up.

        :param request: The current HTTP request.
        :type request: HttpRequest
        :return: True if signups are allowed, False otherwise.
        :rtype: bool
        """

        if hasattr(request, "user") and request.user.is_authenticated:
            return False  # Disable signups for authenticated users

        # Check the ALLOW_SIGNUP setting for unauthenticated users
        return settings.ALLOW_SIGNUP


class TinyUserAccountAdapter(DefaultAccountAdapter, TinyUserAccountAdapterBase):
    pass


class TinyUserDRFAccountAdapter(
    DefaultAccountAdapter, BaseInvitationsAdapter, TinyUserAccountAdapterBase
):
    def format_email_subject(self, subject, context=None):
        """
        Formats the email subject for invitation emails.

        This method is used by the django-invitations package to format the subject of invitation emails.
        It can be overridden to customize the email subject based on the application's needs.

        :param subject: The original email subject template.
        :type subject: str
        :return: The formatted email subject.
        :rtype: str
        """
        if context is None:
            return DefaultAccountAdapter.format_email_subject(self, subject)
        else:
            return BaseInvitationsAdapter.format_email_subject(self, subject, context)
