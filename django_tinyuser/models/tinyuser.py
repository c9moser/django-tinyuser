from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_tinyuser.managers import TinyUserManager
from django_tinyuser.models.userprofile import UserProfile


class TinyUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for the TinyUser application.

    :param AbstractBaseUser: Base class for custom user models.
    :type AbstractBaseUser: django.contrib.auth.models.AbstractBaseUser
    :param PermissionsMixin: Mixin class to add permission fields and methods.
    :type PermissionsMixin: django.contrib.auth.models.PermissionsMixin
    :return: The created user instance.
    :rtype: TinyUser
    """

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

        db_table = "tinyuser_user"

        indexes = [
            models.Index(fields=["email"], name="email_idx"),
            models.Index(fields=["username"], name="username_idx"),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["email"],
                condition=(models.Q(email__isnull=False)),
                name="unique_email",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(email__isnull=True) | models.Q(is_system_user=False)
                ),
                name="email_not_system_user",
            ),
        ]

    #: The email field is used as the unique identifier for authentication
    #: instead of the default username field.
    #:
    #: It is required and must be unique.
    email = models.EmailField(
        unique=True,
        db_column="email",
        verbose_name=_("email address"),
        blank=True,
        null=True,
    )

    #: The username field is a unique identifier for the user, used for display
    #: purposes and as an additional identifier.
    #: It is required and must be unique.

    #: It is required and must be unique.
    username = models.CharField(
        max_length=127, unique=True, db_column="username", verbose_name=_("username")
    )

    #: The is_active field indicates whether the user's account is active.
    #: Inactive accounts may not be able to log in.
    #:
    #: It is a boolean field that defaults to True.
    is_active = models.BooleanField(
        default=True, db_column="is_active", verbose_name=_("active")
    )

    #: The is_staff field indicates whether the user has staff status, which
    #: allows access to the admin site.
    #:
    #: It is a boolean field that defaults to False.
    is_staff = models.BooleanField(
        default=False, db_column="is_staff", verbose_name=_("staff status")
    )

    #: The is_superuser field indicates whether the user has superuser status,
    #: which grants all permissions.
    #:
    #: It is a boolean field that defaults to False.
    is_superuser = models.BooleanField(
        default=False, db_column="is_superuser", verbose_name=_("superuser status")
    )

    is_system_user = models.BooleanField(
        default=False, db_column="is_system_user", verbose_name=_("system user")
    )

    #: The is_verified field indicates whether the user's email address has
    #: been verified. This can be used to restrict access to certain features
    #: until the email is verified.
    #:
    #: It is a boolean field that defaults to False.
    is_verified = models.BooleanField(
        default=False, db_column="is_verified", verbose_name=_("verified")
    )

    #: The joined_at field stores the date and time when the user account was created.
    #: It is automatically set to the current date and time when the user is created.
    joined_at = models.DateTimeField(
        default=timezone.now, db_column="joined_at", verbose_name=_("joined at")
    )

    objects = TinyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    @property
    def display_name(self):
        """
        Returns the display name of the user.

        :return: The display name of the user.
        :rtype: str
        """
        self.profile = getattr(self, "profile", None)
        if not self.profile and self.id:
            try:
                self.profile = UserProfile.objects.filter(user_id=self.id).first()
            except UserProfile.DoesNotExist:
                self.profile = UserProfile.objects.create(
                    user=self, first_name="", last_name="", bio=""
                )

        if self.profile:
            if self.profile.first_name or self.profile.last_name:
                return f"{self.profile.first_name} {self.profile.last_name}".strip()
            elif self.profile.first_name:
                return self.profile.first_name
            elif self.profile.last_name:
                return self.profile.last_name
        return self.username

    def __str__(self):
        return self.username
