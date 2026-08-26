from logging import getLogger

from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext as _

logger = getLogger("django." + __name__)


class TinyUserManager(BaseUserManager):
    """
    Custom user manager for TinyUser model.

    Provides methods to create regular users and superusers.
    """

    def create_user(self, email, username, password=None, **extra_fields):
        """
        Create and save a regular user with the given email, username, and password.

        :param email: The email address of the user.
        :type email: str
        :param username: The username of the user.
        :type username: str
        :param password: The password for the user, defaults to None
        :type password: str, optional
        :raises ValueError: If the email is not provided.
        :raises ValueError: If the username is not provided.
        :return: The created user instance.
        :rtype: TinyUser
        """
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        if not username:
            raise ValueError(_("The Username field must be set"))
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Create and save a superuser with the given email, username, and password.

        :param email: The email address of the superuser.
        :type email: str
        :param username: The username of the superuser.
        :type username: str
        :param password: The password for the superuser, defaults to None
        :type password: str, optional
        :raises ValueError: If is_staff is not True.
        :raises ValueError: If is_superuser is not True.
        :return: The created superuser instance.
        :rtype: TinyUser
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, username, password, **extra_fields)
