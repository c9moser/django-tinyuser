from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings as django_settings

from django_tinyuser import settings
from django_tinyuser.enums import (
    FriendshipStatus,
    FriendshipBlockedStatus
)
from django_tinyuser.managers import (
    FriendshipManager,
    FriendshipRequestManager,
)

from logging import getLogger
logger = getLogger('django.' + __name__)


class FriendshipRequest(models.Model):
    """Model to represent friendship requests between TinyUser instances."""

    class Meta:
        verbose_name = _('friendship request')
        verbose_name_plural = _('friendship requests')

        if settings.AUTH_EXTERNAL_MANAGED:
            managed = False
        else:
            managed = True

        if settings.USE_POSTGRESQL_SCHEMAS:
            db_table = f"{settings.POSTGRESQL_AUTH_SCHEMA}.tinyuser_friendship_request"
        else:
            db_table = 'tinyuser_friendship_request'

        indexes = [
            models.Index(fields=['from_user'], name='request_from_user_idx'),
            models.Index(fields=['to_user'], name='request_to_user_idx'),
            models.Index(fields=['from_user', 'to_user'], name='request_idx'),
        ]
        unique_together = [('from_user', 'to_user'),]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(from_user=models.F('to_user')),
                name='no_self_request'
            ),
            models.CheckConstraint(
                condition=~models.Q(
                    from_user=models.F('to_user'),
                    to_user=models.F('from_user')
                ),
                name='no_duplicate_request'
            ),
        ]

    objects = FriendshipRequestManager()

    #: The from_user field is a foreign key to the TinyUser model, representing the user who
    #: initiated the friendship request.
    #: It is required and will be deleted if the associated user is deleted.
    from_user = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='friendship_requests_sent'
    )

    #: The to_user field is a foreign key to the TinyUser model, representing the user who is the recipient
    #: of the friendship request.
    #:
    #: It is required and will be deleted if the associated user is deleted.
    to_user = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='friendship_requests_received'
    )

    #: The created_at field stores the date and time when the friendship request was created.
    #: It is automatically set to the current date and time when the friendship request is created.
    created_at = models.DateTimeField(default=timezone.now)

    #: The status_data field is a character field that stores the current status of the friendship request as a string.
    #: It is required and has a maximum length of 20 characters. The default value is 'pending'.
    status_data = models.CharField(
        max_length=20,
        default=FriendshipStatus.PENDING.value,
        verbose_name=_('friendship request status'),
        db_column='status'
    )

    @property
    def status(self):
        """
        Return the current status of the friendship request as a FriendshipStatus enum member.

        :return: The current status of the friendship request.
        :rtype: FriendshipStatus
        """
        return FriendshipStatus.from_string(self.status_data)

    @status.setter
    def status(self, value: FriendshipStatus | str):
        """
        Set the status of the friendship request using a FriendshipStatus enum member or a valid string.

        :param value: The new status of the friendship request.
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

    def accept(self):
        """Accept the friendship request by creating a Friendship instance and updating the status."""

        if self.status == FriendshipStatus.PENDING:
            self.status = FriendshipStatus.ACCEPTED
            self.save()

            friendships = FriendshipRequest.objects.filter(
                models.Q(from_user=self.from_user, to_user=self.to_user) |
                models.Q(from_user=self.to_user, to_user=self.from_user)
            )
            if not friendships.exists():
                friendship = Friendship.objects.create(
                    user1=self.from_user,
                    user2=self.to_user,
                    user1_is_initiator=True,
                    status_data=FriendshipStatus.ACCEPTED.value
                )
                friendship.status = FriendshipStatus.ACCEPTED
                friendship.save()
                friendship.refresh_from_db()
                return friendship

            else:
                friendships.update(status_data=FriendshipStatus.ACCEPTED.value)
                friendships.first().refresh_from_db()
                return friendships.first()

        else:
            raise ValueError("Friendship request must be in 'pending' status to be accepted.")

    def reject(self, reason=None):
        """Reject the friendship request by updating the status."""

        friendships = Friendship.objects.filter(
            models.Q(user1=self.from_user, user2=self.to_user)
            | models.Q(user1=self.to_user, user2=self.from_user)
        )
        if self.status in (FriendshipStatus.PENDING, FriendshipStatus.ACCEPTED):

            if friendships.exists():
                friendships.update(status_data=FriendshipStatus.REJECTED.value)
                friendship = friendships.first().refresh_from_db()
            else:
                friendship = Friendship.objects.create(
                    user1=self.from_user,
                    user2=self.to_user,
                    status_data=FriendshipStatus.REJECTED.value
                )
                friendship.status = FriendshipStatus.REJECTED
                friendship.save()
                friendship.refresh_from_db()
        else:
            friendship = friendships.first() if friendships.exists() else None

        self.status = FriendshipStatus.REJECTED
        self.save()
        self.refresh_from_db()

        return friendship


class FriendGroup(models.Model):
    """
    Model to represent groups of friends for TinyUser instances.
    """

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
            models.Index(fields=['name']),
        ]
        unique_together = [('user', 'name'),]

    objects = FriendshipManager()

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


class Friendship(models.Model):
    """Model to represent friendships between TinyUser instances."""
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
            models.Index(fields=['user1'], name='friendship_user1_idx'),
            models.Index(fields=['user2'], name='friendship_user2_idx'),
            models.Index(fields=['user1', 'user2'], name='friendship_idx'),
        ]
        unique_together = [('user1', 'user2'),]

        constraints = [
            models.CheckConstraint(
                condition=~models.Q(user1=models.F('user2')),
                name='no_self_friendship'
            ),
            models.CheckConstraint(
                condition=~models.Q(
                    user1=models.F('user2'),
                    user2=models.F('user1')
                ),
                name='no_duplicate'
            ),
        ]

    objects = FriendshipManager()

    #: The from_user field is a foreign key to the TinyUser model, representing the user who initiated the friendship.
    #: It is required and will be deleted if the associated user is deleted.
    user1 = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='friendships_initiated'
    )

    #: The to_user field is a foreign key to the TinyUser model, representing the user who is
    #: the recipient of the friendship.
    #:
    #: It is required and will be deleted if the associated user is deleted.
    user2 = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='friendships_received'
    )

    #: The is_initiator field indicates whether the user is the initiator of the friendship request.
    #: It is a boolean field that defaults to False.
    user1_is_initiator = models.BooleanField(
        default=False,
        verbose_name=_('friendship initiator'),
        db_column='is_initiator'
    )

    #: The created_at field stores the date and time when the friendship was created.
    #: It is automatically set to the current date and time when the friendship is created.
    created_at = models.DateTimeField(default=timezone.now)

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

    rejected_reason = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('rejection reason'),
        db_column='rejected_reason'
    )

    blocked_status_data = models.CharField(
        max_length=20,
        default=FriendshipBlockedStatus.NOT_BLOCKED.value,
        verbose_name=_('friendship blocked status'),
        db_column='blocked_status'
    )
    blocked_reason_user1 = models.TextField(
        null=True,
        blank=True,
        max_length=500,
        verbose_name=_('blocking reason'),
        db_column='blocked_reason_user1'
    )
    blocked_reason_user2 = models.TextField(
        null=True,
        blank=True,
        max_length=500,
        verbose_name=_('blocking reason'),
        db_column='blocked_reason_user2'
    )

    @property
    def blocked_reason(self, blocking_user):
        """Return the blocking reason for the specified user, or None if not blocked."""
        if self.blocked_status == FriendshipBlockedStatus.BLOCKED_BY_USER1 and blocking_user == self.user1:
            return self.blocked_reason_user1
        elif self.blocked_status == FriendshipBlockedStatus.BLOCKED_BY_USER2 and blocking_user == self.user2:
            return self.blocked_reason_user2
        elif self.blocked_status == FriendshipBlockedStatus.BLOCKED_BY_BOTH:
            if blocking_user == self.user1:
                return self.blocked_reason_user1
            elif blocking_user == self.user2:
                return self.blocked_reason_user2
        return None

    @blocked_reason.setter
    def blocked_reason(self, value, blocking_user):
        """Set the blocking reason for the specified user."""
        if self.blocked_status == FriendshipBlockedStatus.BLOCKED_BY_USER1 and blocking_user == self.user1:
            self.blocked_reason_user1 = value
        elif self.blocked_status == FriendshipBlockedStatus.BLOCKED_BY_USER2 and blocking_user == self.user2:
            self.blocked_reason_user2 = value
        elif self.blocked_status == FriendshipBlockedStatus.BLOCKED_BY_BOTH:
            if blocking_user == self.user1:
                self.blocked_reason_user1 = value
            elif blocking_user == self.user2:
                self.blocked_reason_user2 = value

    @blocked_reason.deleter
    def blocked_reason(self, blocking_user):
        """Delete the blocking reason for the specified user by setting it to None."""
        if self.blocked_status == FriendshipBlockedStatus.BLOCKED_BY_USER1 and blocking_user == self.user1:
            self.blocked_reason_user1 = None
        elif self.blocked_status == FriendshipBlockedStatus.BLOCKED_BY_USER2 and blocking_user == self.user2:
            self.blocked_reason_user2 = None
        elif self.blocked_status == FriendshipBlockedStatus.BLOCKED_BY_BOTH:
            if blocking_user == self.user1:
                self.blocked_reason_user1 = None
            elif blocking_user == self.user2:
                self.blocked_reason_user2 = None

    @property
    def blocked_because(self):
        """Return a string describing the reason for blocking, or None if not blocked."""
        if self.blocked_status == FriendshipBlockedStatus.BLOCKED_BY_USER1:
            return self.blocked_reason_user1
        elif self.blocked_status == FriendshipBlockedStatus.BLOCKED_BY_USER2:
            return self.blocked_reason_user2
        elif self.blocked_status == FriendshipBlockedStatus.BLOCKED_BY_BOTH:
            reasons = []
            if self.blocked_reason_user1:
                reasons.append(f"{self.user1.username}: {self.blocked_reason_user1}")
            if self.blocked_reason_user2:
                reasons.append(f"{self.user2.username}: {self.blocked_reason_user2}")
            return "; ".join(reasons) if reasons else None
        return None

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
    def is_blocked(self):
        """Return True if the friendship is currently blocked, False otherwise."""
        return (
            self.blocked_status != FriendshipBlockedStatus.NOT_BLOCKED
        )

    @property
    def blocked_by(self):
        """Return the user who blocked the friendship, or None if not blocked."""
        if self.blocked_status == FriendshipBlockedStatus.BLOCKED_BY_USER1:
            return self.user1
        elif self.blocked_status == FriendshipBlockedStatus.BLOCKED_BY_USER2:
            return self.user2
        elif self.blocked_status == FriendshipBlockedStatus.BLOCKED_BY_BOTH:
            return [self.user1, self.user2]
        return None

    def accept(self):
        """Accept the friendship request by updating the status."""
        if self.status != FriendshipStatus.PENDING:
            raise ValueError("Friendship must be in 'pending' status to be accepted.")
        self.status = FriendshipStatus.ACCEPTED
        self.save()
        self.refresh_from_db()
        return self

    def reject(self, reason=None):
        """Reject the friendship request by updating the status."""
        if self.status in [FriendshipStatus.PENDING, FriendshipStatus.ACCEPTED]:
            logger.info(f"Friendship between {self.user1} and {self.user2} has been rejected. Reason: {reason}")  # noqa: E501
            self.status = FriendshipStatus.REJECTED
            self.save()
        else:
            logger.warning(f"Attempted to reject a friendship that is not in 'pending' or 'accepted' status. Current status: {self.status}")  # noqa: E501
        self.refresh_from_db()

        return self

    def block(self, blocking_user, reason=None) -> FriendshipBlockedStatus:
        """Block the user by setting the status to 'blocked'."""
        if self.blocked_status == FriendshipBlockedStatus.NOT_BLOCKED:
            if blocking_user == self.user1:
                self.blocked_status = FriendshipBlockedStatus.BLOCKED_BY_USER1
                self.blocked_reason_user1 = reason
            elif blocking_user == self.user2:
                self.blocked_status = FriendshipBlockedStatus.BLOCKED_BY_USER2
                self.blocked_reason_user2 = reason
            else:
                raise ValueError("Blocking user must be either user1 or user2 of the friendship.")
            self.save()
        elif self.blocked_status == FriendshipBlockedStatus.BLOCKED_BY_USER1 and blocking_user == self.user2:
            self.blocked_status = FriendshipBlockedStatus.BLOCKED_BY_BOTH
            self.blocked_reason_user2 = reason
            self.save()
        elif self.blocked_status == FriendshipBlockedStatus.BLOCKED_BY_USER2 and blocking_user == self.user1:
            self.blocked_status = FriendshipBlockedStatus.BLOCKED_BY_BOTH
            self.blocked_reason_user1 = reason
            self.save()

        self.refresh_from_db()
        return self.blocked_status

    def unblock(self, unblocking_user) -> FriendshipBlockedStatus:
        """
        Unblock the user by setting the status back to 'pending'.

        :param unblocking_user: The user who is initiating the unblock action.
        :type unblocking_user: TinyUser or other related user model
        :return: The new blocked status of the friendship after unblocking.
        :rtype: FriendshipBlockedStatus
        """
        if self.blocked_status == FriendshipBlockedStatus.BLOCKED_BY_BOTH:
            if unblocking_user == self.user1:
                self.blocked_status = FriendshipBlockedStatus.BLOCKED_BY_USER2
            elif unblocking_user == self.user2:
                self.blocked_status = FriendshipBlockedStatus.BLOCKED_BY_USER1
            else:
                raise ValueError("Unblocking user must be either user1 or user2 of the friendship.")
            self.save()
        elif self.blocked_status == FriendshipBlockedStatus.BLOCKED_BY_USER1 and unblocking_user == self.user1:
            self.blocked_status = FriendshipBlockedStatus.NOT_BLOCKED
            self.save()
        elif self.blocked_status == FriendshipBlockedStatus.BLOCKED_BY_USER2 and unblocking_user == self.user2:
            self.blocked_status = FriendshipBlockedStatus.NOT_BLOCKED
            self.save()

        self.refresh_from_db()
        return self.blocked_status

    def __str__(self):
        return _("{from_user} is {status} friends with {to_user}").format(
            from_user=self.from_user.username,
            status=self.status.name,
            to_user=self.to_user.username
        )
