from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import markdown
from django_tinyuser import settings
from django_tinyuser.managers import TinyUserManager
from .fields import RestrictedImageField

from django.conf import settings as django_settings


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
        verbose_name = _('user')
        verbose_name_plural = _('users')

        if settings.TINYUSER_EXTERNAL_MANAGED or settings.AUTH_EXTERNAL_MANAGED:
            managed = False
        else:
            managed = True

        if settings.USE_POSTGRESQL_SCHEMAS:
            db_table = f"{settings.POSTGRESQL_AUTH_SCHEMA}.tinyuser_user"
        else:
            db_table = 'tinyuser_user'

        indexes = [
            models.Index(fields=['email'], name='email_idx'),
            models.Index(fields=['username'], name='username_idx'),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=['email'],
                condition=(models.Q(email__isnull=False)),
                name='unique_email'
            ),
            models.CheckConstraint(
                condition=(models.Q(email__isnull=True) | models.Q(is_system_user=False)),
                name='email_not_system_user'
            ),
        ]

    #: The email field is used as the unique identifier for authentication
    #: instead of the default username field.
    #:
    #: It is required and must be unique.
    email = models.EmailField(
        unique=True,
        db_column='email',
        verbose_name=_('email address'),
        blank=True,
        null=True,
    )

    #: The username field is a unique identifier for the user, used for display
    #: purposes and as an additional identifier.
    #: It is required and must be unique.

    #: It is required and must be unique.
    username = models.CharField(
        max_length=127,
        unique=True,
        db_column='username',
        verbose_name=_('username')
    )

    #: The is_active field indicates whether the user's account is active.
    #: Inactive accounts may not be able to log in.
    #:
    #: It is a boolean field that defaults to True.
    is_active = models.BooleanField(
        default=True,
        db_column='is_active',
        verbose_name=_('active')
    )

    #: The is_staff field indicates whether the user has staff status, which
    #: allows access to the admin site.
    #:
    #: It is a boolean field that defaults to False.
    is_staff = models.BooleanField(
        default=False,
        db_column='is_staff',
        verbose_name=_('staff status')
    )

    #: The is_superuser field indicates whether the user has superuser status,
    #: which grants all permissions.
    #:
    #: It is a boolean field that defaults to False.
    is_superuser = models.BooleanField(
        default=False,
        db_column='is_superuser',
        verbose_name=_('superuser status')
    )

    is_system_user = models.BooleanField(
        default=False,
        db_column='is_system_user',
        verbose_name=_('system user')
    )

    #: The is_verified field indicates whether the user's email address has
    #: been verified. This can be used to restrict access to certain features
    #: until the email is verified.
    #:
    #: It is a boolean field that defaults to False.
    is_verified = models.BooleanField(
        default=False,
        db_column='is_verified',
        verbose_name=_('verified')
    )

    #: The joined_at field stores the date and time when the user account was created.
    #: It is automatically set to the current date and time when the user is created.
    joined_at = models.DateTimeField(
        default=timezone.now,
        db_column='joined_at',
        verbose_name=_('joined at')
    )

    objects = TinyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    @property
    def display_name(self):
        """
        Returns the display name of the user.

        :return: The display name of the user.
        :rtype: str
        """
        self.profile = getattr(self, 'profile', None)
        if not self.profile and self.id:
            try:
                self.profile = TinyUserProfile.objects.filter(user_id=self.id).first()
            except TinyUserProfile.DoesNotExist:
                self.profile = TinyUserProfile.objects.create(user=self,
                                                              first_name='',
                                                              last_name='',
                                                              bio='')

        if self.profile:
            if (self.profile.first_name or self.profile.last_name):
                return f"{self.profile.first_name} {self.profile.last_name}".strip()
            elif self.profile.first_name:
                return self.profile.first_name
            elif self.profile.last_name:
                return self.profile.last_name
        return self.username

    def __str__(self):
        return self.username


class TinyUserProfile(models.Model):
    """Model to store additional profile information for TinyUser."""

    #: The user field is a one-to-one relationship with the TinyUser model, linking each profile to a specific user.
    #: It is required and will be deleted if the associated user is deleted.
    user = models.OneToOneField(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile')

    #: The first_name field stores the user's first name.
    #: It is optional and can be left blank.
    first_name = models.CharField(
        max_length=30,
        blank=True,
    )
    #: The last_name field stores the user's last name.
    #: It is optional and can be left blank.
    last_name = models.CharField(max_length=30, blank=True)

    #: The bio field allows users to provide a short biography or description
    #: about themselves. It is optional and can be left blank.
    bio = models.TextField(blank=True, verbose_name=_('biography (Markdown supported)'))

    #: The location field allows users to specify their location. It is optional and can be left blank.
    location = models.CharField(max_length=255, blank=True, verbose_name=_('location'))

    #: The website field allows users to provide a URL to their personal website or social media profile.
    #: It is optional and can be left blank.
    website = models.URLField(blank=True, verbose_name=_('website'))

    #: The birth_date field allows users to specify their date of birth. It is optional and can be left blank.
    birth_date = models.DateField(blank=True, null=True, verbose_name=_('birth date'))

    #: The profile_picture fields allows users to upload a profile picture. It is optional and can be left blank.
    profile_picture_small = RestrictedImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        max_file_size=1024 * 1024,  # 1 MiB
        verbose_name=_('small profile picture')
    )

    profile_picture_medium = RestrictedImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        max_file_size=int(2.5 * 1024 * 1024),  # 2.5 MiB
        verbose_name=_('medium profile picture')
    )

    profile_picture_large = RestrictedImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        max_file_size=int(5 * 1024 * 1024),  # 5 MiB
        verbose_name=_('large profile picture')
    )

    @property
    def bio_html(self):
        """
        Return the bio field rendered as HTML using Markdown.

        :return: The bio field rendered as HTML.
        :rtype: SafeString
        """

        from django.utils.safestring import mark_safe
        return mark_safe(markdown.markdown(self.bio, extensions=['extra', 'nl2br']))

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')

        if settings.AUTH_EXTERNAL_MANAGED:
            managed = False
        else:
            managed = True

        if settings.USE_POSTGRESQL_SCHEMAS:
            db_table = f"{settings.POSTGRESQL_AUTH_SCHEMA}.tinyuser_profile"
        else:
            db_table = 'tinyuser_profile'
        indexes = [
            models.Index(fields=['user'], name='user_idx'),
        ]
