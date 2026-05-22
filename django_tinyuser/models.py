from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings as django_settings
from django_tinyuser import settings
from django_tinyuser.managers import TinyUserManager
from django_tinyuser.enums import (
    FriendshipStatus,
    FriendshipBlockedStatus
)


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
    bio = models.TextField(blank=True)

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


class UserFriendGroup(models.Model):
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

    user = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_friend_groups'
    )

    #: The members field is a many-to-many relationship with the TinyUser model,
    #: allowing multiple users to be part of the same friend group.
    members = models.ManyToManyField(django_settings.AUTH_USER_MODEL, related_name='friend_groups')

    def add_member(self, user):
        """Add a user to the friend group.

        :param user: The user to be added to the friend group.
        :type user: TinyUser
        """
        self.members.add(user)

    def remove_member(self, user):
        """Remove a user from the friend group.

        :param user: The user to be removed from the friend group.
        :type user: TinyUser
        """
        self.members.remove(user)

    def is_member(self, user):
        """Check if a user is a member of the friend group.

        :param user: The user to check for membership in the friend group.
        :type user: TinyUser
        :return: True if the user is a member of the friend group, False otherwise.
        :rtype: bool
        """
        if self.owner == user:
            return True
        return self.members.filter(id=user.id).exists()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('friend group')
        verbose_name_plural = _('friend groups')

        if settings.AUTH_EXTERNAL_MANAGED:
            managed = False
        else:
            managed = True

        if settings.USE_POSTGRESQL_SCHEMAS:
            db_table = f"{settings.POSTGRESQL_AUTH_SCHEMA}.tinyuser_friend_group"
        else:
            db_table = 'tinyuser_friend_group'
        indexes = [
            models.Index(fields=['name'], name='friend_group_name_idx'),
        ]
        unique_together = [('user', 'name'),]


class UserFriendship(models.Model):
    """Model to represent friendships between TinyUser instances."""

    #: The from_user field is a foreign key to the TinyUser model, representing the user who initiated the friendship.
    #: It is required and will be deleted if the associated user is deleted.
    from_user = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='friendships_initiated'
    )

    #: The to_user field is a foreign key to the TinyUser model, representing the user who is
    #: the recipient of the friendship.
    #:
    #: It is required and will be deleted if the associated user is deleted.
    to_user = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='friendships_received'
    )

    #: The is_initiator field indicates whether the user is the initiator of the friendship request.
    #: It is a boolean field that defaults to False.
    is_initiator = models.BooleanField(
        default=False,
        verbose_name=_('friendship initiator'),
        db_column='is_initiator'
    )

    @property
    def is_recipient(self):
        """Return True if the user is the recipient of the friendship, False otherwise."""
        return not self.is_initiator

    #: The created_at field stores the date and time when the friendship was created.
    #: It is automatically set to the current date and time when the friendship is created.
    created_at = models.DateTimeField(default=timezone.now)

    #: The status field indicates the status of the friendship, such as 'pending', 'accepted', 'rejected' or 'blocked'.
    #: It is a character field with a maximum length of 20 characters, and it defaults to 'pending'.
    status_data = models.CharField(
        max_length=20,
        default=FriendshipStatus.PENDING.value,
        verbose_name=_('friendship status'),
        db_column='status'
    )

    @property
    def status(self):
        """
        Return the current status of the friendship as a FriendshipStatus enum member.
        :return: The current status of the friendship.
        :rtype: FriendshipStatus
        """
        return FriendshipStatus.from_string(self.status_data)

    @status.setter
    def status(self, value: FriendshipStatus | str):
        """
        Set the status of the friendship using a FriendshipStatus enum member or a valid string.
        :param value: The new status of the friendship.
        :type value: FriendshipStatus or str
        """
        if isinstance(value, FriendshipStatus):
            self.status_data = value.value
        elif isinstance(value, str):
            try:
                self.status_data = FriendshipStatus.from_string(value).value
            except ValueError:
                raise ValueError(f"Invalid status value: {value}. Must be a valid FriendshipStatus or string.")
        else:
            raise TypeError("Status must be a FriendshipStatus enum member or a valid string.")

    blocked_status_data = models.CharField(
        max_length=20,
        default=FriendshipBlockedStatus.NOT_BLOCKED.value,
        verbose_name=_('friendship blocked status'),
        db_column='blocked_status'
    )

    @property
    def blocked_status(self):
        """
        Return the current blocked status of the friendship as a FriendshipBlockedStatus enum member.
        :return: The current blocked status of the friendship.
        :rtype: FriendshipBlockedStatus
        """
        return FriendshipBlockedStatus.from_string(self.blocked_status_data)

    @blocked_status.setter
    def blocked_status(self, value: FriendshipBlockedStatus | str):
        """
        Set the blocked status of the friendship using a FriendshipBlockedStatus enum member or a valid string.
        :param value: The new blocked status of the friendship.
        :type value: FriendshipBlockedStatus or str
        """
        if isinstance(value, FriendshipBlockedStatus):
            self.blocked_status_data = value.value
        elif isinstance(value, str):
            try:
                self.blocked_status_data = FriendshipBlockedStatus.from_string(value).value
            except ValueError:
                raise ValueError(f"Invalid blocked status value: {value}. Must be a valid FriendshipBlockedStatus or string.")  # noqa: E501
        else:
            raise TypeError("Blocked status must be a FriendshipBlockedStatus enum member or a valid string.")

    @blocked_status.deleter
    def blocked_status(self):
        """Delete the blocked status of the friendship by setting it to 'not blocked'."""
        self.blocked_status_data = FriendshipBlockedStatus.NOT_BLOCKED.value

    @property
    def is_pending(self):
        """Return True if the friendship is currently pending, False otherwise."""
        return self.status == FriendshipStatus.PENDING

    @property
    def is_accepted(self):
        """Return True if the friendship is currently accepted, False otherwise."""
        others = self.__class__.objects.filter(from_user=self.to_user, to_user=self.from_user)
        if others.exists():
            return (
                self.status == FriendshipStatus.ACCEPTED
                and others[0].status == FriendshipStatus.ACCEPTED
            )
        return False

    @property
    def is_rejected(self):
        """Return True if the friendship is currently rejected, False otherwise."""
        other_status = self.__class__.objects.filter(from_user=self.to_user, to_user=self.from_user)[0].status
        return self.status == FriendshipStatus.REJECTED or other_status == FriendshipStatus.REJECTED

    @property
    def is_blocked(self):
        """Return True if the friendship is currently blocked, False otherwise."""
        other_status = self.__class__.objects.filter(from_user=self.to_user, to_user=self.from_user)[0].status
        return (
            self.blocked_status != FriendshipBlockedStatus.NOT_BLOCKED
            or other_status != FriendshipBlockedStatus.NOT_BLOCKED
        )

    def accept(self):
        """Accept the friendship request by setting the status to 'accepted'."""
        if self.is_initiator:
            raise ValueError(_('Only the recipient of a friendship request can accept it.'))

        self.status_data = FriendshipStatus.ACCEPTED.value
        self.other_status = self.__class__.objects.get_or_create(
            from_user=self.to_user,
            to_user=self.from_user
        )[0]

        if self.other_status.status == FriendshipStatus.PENDING:
            self.other_status.status_data = FriendshipStatus.ACCEPTED.value
            self.other_status.save()

        self.save()

    def reject(self):
        """Reject the friendship request by setting the status to 'rejected'."""
        self.status_data = FriendshipStatus.REJECTED.value
        self.other_status = self.__class__.objects.get_or_create(
            from_user=self.to_user,
            to_user=self.from_user
        )[0]
        self.other_status.status_data = FriendshipStatus.REJECTED.value
        self.other_status.save()
        self.save()

    def block(self):
        """Block the user by setting the status to 'blocked'."""
        self.blocked_status = FriendshipBlockedStatus.BLOCKED_BY_FROM_USER
        self.block_initiator = True
        self.save()

        friendship2 = self.__class__.objects.filter(
            from_user=self.to_user,
            to_user=self.from_user
        )[0]
        if friendship2 and friendship2.blocked_status == FriendshipBlockedStatus.NOT_BLOCKED:
            friendship2.blocked_status = FriendshipBlockedStatus.BLOCKED_BY_TO_USER
            friendship2.save()

    def unblock(self):
        """Unblock the user by setting the status back to 'pending'."""
        self.blocked_status = FriendshipBlockedStatus.NOT_BLOCKED
        self.block_initiator = False
        self.save()

        friendship2 = self.__class__.objects.filter(
            from_user=self.to_user,
            to_user=self.from_user
        )[0]
        if friendship2 and friendship2.blocked_status == FriendshipBlockedStatus.BLOCKED_BY_TO_USER:
            friendship2.blocked_status = FriendshipBlockedStatus.NOT_BLOCKED
            friendship2.save()

    def __str__(self):
        return _("{from_user} is {status} friends with {to_user}").format(
            from_user=self.from_user.username,
            status=self.status.name,
            to_user=self.to_user.username
        )

    class Meta:
        verbose_name = _('user friendship')
        verbose_name_plural = _('user friendships')

        if settings.AUTH_EXTERNAL_MANAGED:
            managed = False
        else:
            managed = True

        if settings.USE_POSTGRESQL_SCHEMAS:
            db_table = f"{settings.POSTGRESQL_AUTH_SCHEMA}.tinyuser_friendship"
        else:
            db_table = 'tinyuser_friendship'

        indexes = [
            models.Index(fields=['from_user'], name='from_user_idx'),
            models.Index(fields=['to_user'], name='to_user_idx'),
            models.Index(fields=['from_user', 'to_user'], name='friendship_idx'),
        ]
        unique_together = [('from_user', 'to_user'),]
