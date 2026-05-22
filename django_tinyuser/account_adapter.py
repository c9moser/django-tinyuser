from allauth.account.adapter import DefaultAccountAdapter
from django.http import HttpRequest
from django_tinyuser import settings
from django_tinyuser.models import TinyUser
from django.forms import Form


class TinyUserAccountAdapter(DefaultAccountAdapter):

    def save_user(self,
                  request: HttpRequest,
                  user: TinyUser,
                  form: Form,
                  commit: bool = True):
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

    def allow_signup(self, request):
        # Override this method to control whether signups are allowed
        if hasattr(request, 'user') and request.user.is_authenticated:
            return False  # Disable signups for authenticated users

        return settings.ALLOW_SIGNUP
