from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


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
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        if not username:
            raise ValueError(_('The Username field must be set'))
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
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, username, password, **extra_fields)


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

    #: The email field is used as the unique identifier for authentication
    #: instead of the default username field.
    #:
    #: It is required and must be unique.
    email = models.EmailField(
        unique=True,
        db_column='email_address',
        verbose_name=_('email address')
    )

    #: The username field is a unique identifier for the user, used for display
    #: purposes and as an additional identifier.
    #:
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

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

        db_table = 'tinyuser_user'

        indexes = [
            models.Index(fields=['email'], name='email_idx'),
            models.Index(fields=['username'], name='username_idx'),
        ]


class TinyUserProfile(models.Model):
    """Model to store additional profile information for TinyUser."""

    #: The user field is a one-to-one relationship with the TinyUser model, linking each profile to a specific user.
    #: It is required and will be deleted if the associated user is deleted.
    user = models.OneToOneField(
        TinyUser,
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
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')

        db_table = 'tinyuser_profile'
        indexes = [
            models.Index(fields=['user'], name='user_idx'),
        ]


class UserGroup(models.Model):
    """Model to represent groups of friends for TinyUser instances."""

    #: The name field is a character field that stores the name of the friend group.
    #: It is required and has a maximum length of 255 characters.
    name = models.CharField(max_length=255)

    description_type = models.TextField(_('description type'),
                                        default='text',
                                        choices=[
                                            ('text', _('Text')),
                                            ('markdown', _('Markdown')),
                                            ('bbcode', _('BBCode'))
                                        ])

    #: The description field is a text field that allows users to provide a description of the friend group.
    #: It is optional and can be left blank.
    description = models.TextField(blank=True)

    owner = models.ForeignKey(
        TinyUser,
        on_delete=models.CASCADE,
        related_name='owned_friend_groups'
    )

    #: The members field is a many-to-many relationship with the TinyUser model,
    #: allowing multiple users to be part of the same friend group.
    members = models.ManyToManyField(TinyUser, related_name='friend_groups')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('friend group')
        verbose_name_plural = _('friend groups')

        db_table = 'tinyuser_friend_group'
        indexes = [
            models.Index(fields=['name'], name='friend_group_name_idx'),
        ]


class UserFriendship(models.Model):
    """Model to represent friendships between TinyUser instances."""

    #: The from_user field is a foreign key to the TinyUser model, representing the user who initiated the friendship.
    #: It is required and will be deleted if the associated user is deleted.
    from_user = models.ForeignKey(
        TinyUser,
        on_delete=models.CASCADE,
        related_name='friendships_initiated'
    )

    #: The to_user field is a foreign key to the TinyUser model, representing the user who is the recipient of the friendship.
    #: It is required and will be deleted if the associated user is deleted.
    to_user = models.ForeignKey(
        TinyUser,
        on_delete=models.CASCADE,
        related_name='friendships_received'
    )

    #: The created_at field stores the date and time when the friendship was created.
    #: It is automatically set to the current date and time when the friendship is created.
    created_at = models.DateTimeField(default=timezone.now)

    #: The status field indicates the status of the friendship, such as 'pending', 'accepted', or 'rejected'.
    #: It is a character field with a maximum length of 20 characters, and it defaults to 'pending'.
    status = models.CharField(max_length=20, default='pending')

    def accept(self):
        """Accept the friendship request by setting the status to 'accepted'."""
        self.status = 'accepted'
        self.save()

    def reject(self):
        """Reject the friendship request by setting the status to 'rejected'."""
        self.status = 'rejected'
        self.save()

    def __str__(self):
        return f"{self.from_user.username} is friends with {self.to_user.username}"

    class Meta:
        verbose_name = _('user friendship')
        verbose_name_plural = _('user friendships')

        db_table = 'tinyuser_friendship'
        indexes = [
            models.Index(fields=['from_user'], name='from_user_idx'),
            models.Index(fields=['to_user'], name='to_user_idx'),
            models.Index(fields=['from_user', 'to_user'], name='friendship_idx'),
        ]
