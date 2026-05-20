from django.contrib.auth.models import BaseUserManager
from django.db.models import Manager, Q
from django.utils.translation import gettext as _

from django_tinyuser.enums import (
    FriendshipStatus,
    FriendshipBlockedStatus
)


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


class FriendshipManager(Manager):
    """
    Custom manager for the Friendship model.

    Provides methods to manage friendships between users, such as creating, accepting, rejecting, and blocking friendships.
    """

    def create_friendship(self, from_user, to_user):
        """
        Create a new friendship request from one user to another.

        :param from_user: The user who is sending the friendship request.
        :type from_user: TinyUser
        :param to_user: The user who is receiving the friendship request.
        :type to_user: TinyUser
        :return: The created Friendship instance.
        :rtype: Friendship
        """
        if from_user == to_user:
            raise ValueError(_('Users cannot be friends with themselves.'))
        if self.filter(from_user=from_user, to_user=to_user).exists():
            raise ValueError(_('Friendship request already exists.'))
        if self.filter(from_user=to_user, to_user=from_user).exists():
            raise ValueError(_('A friendship request from the other user already exists.'))

        friendship = self.model(from_user=from_user, to_user=to_user)
        friendship.save(using=self._db)
        return friendship

    @property
    def pending_friendships(self, user):
        """
        Return a queryset of all pending friendship requests.

        :return: A queryset of pending friendships.
        :rtype: QuerySet
        """
        return self.filter(
            Q(from_user=user) | Q(to_user=user),
            status_data=FriendshipStatus.PENDING.value
        )

    @property
    def accepted_friendships(self, user):
        """
        Return a queryset of all accepted friendships.

        :return: A queryset of accepted friendships.
        :rtype: QuerySet
        """
        return self.filter(
            Q(from_user=user) | Q(to_user=user),
            status_data=FriendshipStatus.ACCEPTED.value
        )

    @property
    def rejected_friendships(self, user):
        """
        Return a queryset of all rejected friendships.

        :return: A queryset of rejected friendships.
        :rtype: QuerySet
        """
        return self.filter(
            Q(from_user=user) | Q(to_user=user),
            status_data=FriendshipStatus.REJECTED.value
        )

    @property
    def blocked_friendships(self, user):
        """
        Return a queryset of all blocked friendships.

        :return: A queryset of blocked friendships.
        :rtype: QuerySet
        """
        return self.filter(
            Q(from_user=user) | Q(to_user=user),
            status_data=FriendshipStatus.BLOCKED.value
        )

    @property
    def all_friendships(self, user):
        """
        Return a queryset of all friendships for a given user.

        :return: A queryset of all friendships.
        :rtype: QuerySet
        """
        return self.filter(
            Q(from_user=user) | Q(to_user=user)
        )

    @property
    def friends(self, user):
        """
        Return a list of all friends for a given user.

        :return: A list of friends.
        :rtype: list
        """
        return [
            f.to_user if f.from_user == user else f.from_user
            for f in self.filter(
                Q(from_user=user) | Q(to_user=user),
                status_data=FriendshipStatus.ACCEPTED.value
            )
        ]

    @property
    def friend_requests(self, user):
        """
        Return a queryset of all incoming friendship requests for a given user.

        :return: A queryset of incoming friendship requests.
        :rtype: list
        """
        return self.filter(
            to_user=user,
            status_data=FriendshipStatus.PENDING.value
        )

    @property
    def blocked_by_user(self, user):
        """
        Return a list of all users who have blocked the given user.

        :return: A list of users who have blocked the given user.
        :rtype: list
        """
        return [
            from_user if from_user != user else to_user
            for from_user, to_user in
            self.filter((
                (Q(from_user=user) & Q(blocked_status_data=FriendshipBlockedStatus.BLOCKED_BY_FROM_USER.value))
                | (Q(to_user=user) & Q(blocked_status_data=FriendshipBlockedStatus.BLOCKED_BY_TO_USER.value))
            )).values_list('from_user', 'to_user')
        ]

    @property
    def blocked_from_users(self, user):
        """
        Return a list of all users that the given user has blocked.

        :return: A list of users that the given user has blocked.
        :rtype: list
        """
        return [
            to_user if from_user == user else from_user
            for from_user, to_user in
            self.filter((
                (Q(from_user=user) & Q(blocked_status_data=FriendshipBlockedStatus.BLOCKED_BY_TO_USER.value))
                | (Q(to_user=user) & Q(blocked_status_data=FriendshipBlockedStatus.BLOCKED_BY_FROM_USER.value))
            )).values_list('from_user', 'to_user')
        ]
