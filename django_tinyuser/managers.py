from django.contrib.auth.models import BaseUserManager
from django.db.models import Manager, Q
from django.utils.translation import gettext as _

from django_tinyuser.enums import (
    FriendshipStatus,
    FriendshipBlockedStatus
)
from django_tinyuser.exceptions import (
    FriendshipPending,
    FriendshipAlreadyExists
)


from logging import getLogger
logger = getLogger('django.' + __name__)


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


class FriendshipRequestManager(Manager):
    """
    Custom manager for the FriendshipRequest model.

    Provides methods to manage friendship requests between users, such as creating,
    accepting, rejecting, and blocking requests.
    """

    def create_friendship_request(self, from_user, to_user):
        """
        Create a new friendship request from one user to another.

        :param from_user: The user who is sending the friendship request.
        :type from_user: TinyUser
        :param to_user: The user who is receiving the friendship request.
        :type to_user: TinyUser
        :return: The created FriendshipRequest instance.
        :rtype: FriendshipRequest
        """
        if from_user == to_user:
            raise ValueError(_('Users cannot send friendship requests to themselves.'))
        if self.filter(from_user=from_user, to_user=to_user).exists():
            raise FriendshipAlreadyExists(_('Friendship request already exists.'))
        if self.filter(from_user=to_user, to_user=from_user).exists():
            if self.filter(from_user=to_user, to_user=from_user, status=FriendshipStatus.PENDING.value).exists():
                raise FriendshipPending(_('A friendship request from the other user already exists.'))
            else:
                raise FriendshipAlreadyExists(_('A friendship request from the other user already exists.'))

        friendship_request = self.model(from_user=from_user, to_user=to_user)
        friendship_request.save(using=self._db)
        return friendship_request


class FriendshipManager(Manager):
    """
    Custom manager for the Friendship model.

    Provides methods to manage friendships between users, such as creating, accepting,
    rejecting, and blocking friendships.
    """

    def create_friendship(self, user1, user2, status=FriendshipStatus.PENDING):
        """
        Create a new friendship request from one user to another.

        :param user1: The user who is sending the friendship request.
        :type user1: TinyUser
        :param user2: The user who is receiving the friendship request.
        :type user2: TinyUser
        :return: The created Friendship instance.
        :rtype: Friendship
        """
        from django_tinyuser.models import FriendshipRequest

        if user1 == user2:
            raise ValueError(_('Users cannot be friends with themselves.'))
        if self.filter(user1=user1, user2=user2).exists():
            raise FriendshipAlreadyExists(_('Friendship request already exists.'))
        if self.filter(user1=user2, user2=user1).exists():
            raise FriendshipAlreadyExists(_('A friendship request from the other user already exists.'))

        friendship = self.model(user1=user1, user2=user2, status=status.value)
        friendship.save(using=self._db)

        friendship_requests = FriendshipRequest.objects.filter(
            Q(from_user=user1, to_user=user2) |
            Q(from_user=user2, to_user=user1)
        )
        if not friendship_requests.exists():
            FriendshipRequest.objects.create(from_user=user1, to_user=user2)
        else:
            friendship_requests.update(status=FriendshipStatus.PENDING.value)

        return friendship

    def reject_friendship(self, user1, user2, reason=None):
        """
        Reject a friendship request between two users.

        :param user1: The user who sent the friendship request.
        :type user1: TinyUser
        :param user2: The user who received the friendship request.
        :type user2: TinyUser
        :return: The updated Friendship instance with the rejected status.
        :rtype: Friendship
        """
        from django_tinyuser.models import FriendshipRequest

        friendships = self.filter(
            Q(user1=user1, user2=user2) |
            Q(user1=user2, user2=user1),
        )
        if friendships.exists():
            friendships.update(status=FriendshipStatus.REJECTED.value)
            friendship = friendships.first()
            friendship.refresh_from_db()  # Refresh the instance to get the updated status
        else:
            friendship = self.model(
                user1=user1, user2=user2,
                status_data=FriendshipStatus.REJECTED.value
            )
            friendship.save(using=self._db)
            friendship.refresh_from_db()  # Refresh the instance to get the updated status

        friendship_request = FriendshipRequest.objects.filter(
            Q(from_user=user1, to_user=user2) |
            Q(from_user=user2, to_user=user1),
        )

        if friendship_request.exists():
            friendship_request.update(status_data=FriendshipStatus.REJECTED.value)
        else:
            logger.warning(
                f"No existing friendship request found between {user1} and {user2} to reject."
                "Creating a new rejected friendship request."
            )
            FriendshipRequest.objects.create(
                from_user=user1,
                to_user=user2,
                status_data=FriendshipStatus.REJECTED.value
            )

        return friendship

    def pending_friendships(self, user):
        """
        Return a queryset of all pending friendship requests.

        :param user: The user for whom to retrieve pending friendship requests.
        :type user: TinyUser
        :return: A queryset of pending friendships.
        :rtype: QuerySet
        """
        return self.filter(
            Q(user1=user) | Q(user2=user),
            status_data=FriendshipStatus.PENDING.value
        )

    def accepted_friendships(self, user):
        """
        Return a queryset of all accepted friendships.

        :param user: The user for whom to retrieve accepted friendships.
        :type user: TinyUser
        :return: A queryset of accepted friendships.
        :rtype: QuerySet
        """
        return self.filter(
            Q(user1=user) | Q(user2=user),
            status_data=FriendshipStatus.ACCEPTED.value
        )

    def rejected_friendships(self, user):
        """
        Return a queryset of all rejected friendships.

        :param user: The user for whom to retrieve rejected friendships.
        :type user: TinyUser
        :return: A queryset of rejected friendships.
        :rtype: QuerySet
        """
        return self.filter(
            Q(user1=user) | Q(user2=user),
            status_data=FriendshipStatus.REJECTED.value
        )

    def blocked_friendships(self, user):
        """
        Return a queryset of all blocked friendships.

        :param user: The user for whom to retrieve blocked friendships.
        :type user: TinyUser
        :return: A queryset of blocked friendships.
        :rtype: QuerySet
        """
        return self.friendships(user).filter(
            Q(user1=user) | Q(user2=user),
            blocked_status_data__ne=FriendshipBlockedStatus.NOT_BLOCKED.value
        )

    def all_friendships(self, user):
        """
        Return a queryset of all friendships for a given user.

        :param user: The user for whom to retrieve all friendships.
        :type user: TinyUser
        :return: A queryset of all friendships.
        :rtype: QuerySet
        """
        return self.filter(
            Q(user1=user) | Q(user2=user)

        )

    def friendships(self, user):
        """
        Return a queryset of all active friendships.

        :param user: The user for whom to retrieve active friendships.
        :type user: TinyUser
        :return: A queryset of all active friendships.
        :rtype: QuerySet
        """
        return self.all_friendships(user).filter(
            blocked_status_data=FriendshipBlockedStatus.NOT_BLOCKED.value,
            friendship_status_data=FriendshipStatus.ACCEPTED.value
        )

    def friends(self, user):
        """
        Return a list of all friends for a given user.

        :param user: The user for whom to retrieve friends.
        :type user: TinyUser
        :return: A list of friends.
        :rtype: list
        """
        return [
            f.user2 if f.user1 == user else f.user1
            for f in self.filter(
                Q(user1=user) | Q(user2=user),
                status_data=FriendshipStatus.ACCEPTED.value
            )
        ]

    def friend_requests(self, user):
        """
        Return a queryset of all incoming friendship requests for a given user.

        :param user: The user for whom to retrieve incoming friendship requests.
        :type user: TinyUser
        :return: A queryset of incoming friendship requests.
        :rtype: QuerySet
        """
        return self.filter(
            to_user=user,
            status_data=FriendshipStatus.PENDING.value
        )

    def blocked_by_user(self, user):
        """
        Return a list of all users who have blocked the given user.

        :param user: The user for whom to retrieve users who have blocked them.
        :type user: TinyUser
        :return: A list of users who have blocked the given user.
        :rtype: list
        """
        return [
            from_user if from_user != user else to_user
            for from_user, to_user in
            self.filter((
                (Q(user1=user) & Q(blocked_status_data=FriendshipBlockedStatus.BLOCKED_BY_USER1.value))
                | (Q(user2=user) & Q(blocked_status_data=FriendshipBlockedStatus.BLOCKED_BY_USER2.value))
            )).values_list('user1', 'user2')
        ]

    def blocked_from_users(self, user):
        """
        Return a list of all users that the given user has blocked.

        :param user: The user for whom to retrieve blocked users.
        :type user: TinyUser
        :return: A list of users that the given user has blocked.
        :rtype: list
        """
        return [
            to_user if from_user == user else from_user
            for from_user, to_user in
            self.filter((
                (Q(user1=user) & Q(blocked_status_data=FriendshipBlockedStatus.BLOCKED_BY_USER1.value))
                | (Q(user2=user) & Q(blocked_status_data=FriendshipBlockedStatus.BLOCKED_BY_USER2.value))
            )).values_list('user1', 'user2')
        ]
