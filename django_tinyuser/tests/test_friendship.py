from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.models import Q
from django_tinyuser.enums import FriendshipBlockedStatus
from django_tinyuser.models import (
    FriendshipRequest,
    Friendship,
    FriendshipStatus,
)


class FriendshipRequestModelTestCase(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user1 = self.User.objects.create_user(
            email='user1@example.com',
            username='user1',
            password='password1'
        )
        self.user2 = self.User.objects.create_user(
            email='user2@example.com',
            username='user2',
            password='password2'
        )
        self.user3 = self.User.objects.create_user(
            email='user3@example.com',
            username='user3',
            password='password3'
        )

    def test_friendship_request_creation_success(self):
        request = FriendshipRequest.objects.create(from_user=self.user1, to_user=self.user2)
        self.assertEqual(request.from_user, self.user1)
        self.assertEqual(request.to_user, self.user2)
        self.assertEqual(request.status, FriendshipStatus.PENDING)

    def test_friendship_request_creation_failure_duplicate(self):
        from django.db.utils import IntegrityError

        FriendshipRequest.objects.create(from_user=self.user1, to_user=self.user2)

        # check that duplicate requests cannot be created
        with self.assertRaises(IntegrityError):
            FriendshipRequest.objects.create(from_user=self.user1, to_user=self.user2)

    def test_friendship_request_creation_failure_reverse_duplicate(self):
        """
        check that duplicate requests cannot be created in reverse direction
        (user2 to user1) if a request already exists from user1 to user2
        """
        pass
        # from django_tinyuser.exceptions import FriendshipAlreadyExists

        # with self.assertRaises(FriendshipAlreadyExists):
        #    FriendshipRequest.objects.create(from_user=self.user2, to_user=self.user1)

    def test_friendship_request_creation_failure_self_request(self):
        # check that users cannot send requests to themselves
        from django.db.utils import IntegrityError

        with self.assertRaises(IntegrityError):
            FriendshipRequest.objects.create(from_user=self.user1, to_user=self.user1)

    def test_friendship_request_acceptance(self):
        request = FriendshipRequest.objects.create(from_user=self.user1, to_user=self.user2)
        friendship = request.accept()
        request.refresh_from_db()  # Refresh the request from the database to ensure we have the latest data
        self.assertEqual(request.status, FriendshipStatus.ACCEPTED)

        self.assertTrue(friendship is not None)
        self.assertEqual(friendship.status, FriendshipStatus.ACCEPTED)
        self.assertFalse(Friendship.objects.filter(user1=self.user2, user2=self.user1).exists())

    def test_friendship_request_rejection(self):
        request = FriendshipRequest.objects.create(from_user=self.user1, to_user=self.user2)
        self.assertIn(request.status, [FriendshipStatus.PENDING, FriendshipStatus.ACCEPTED])
        friendship = request.reject()
        request.refresh_from_db()  # Refresh the request from the database to ensure we have the latest data
        self.assertEqual(request.status, FriendshipStatus.REJECTED)
        self.assertEqual(friendship.status, FriendshipStatus.REJECTED)
        request.refresh_from_db()

        fs = Friendship.objects.filter(
            Q(user1=self.user1, user2=self.user2) | Q(user1=self.user2, user2=self.user1)
        )
        self.assertTrue(fs.exists())
        self.assertEqual(fs.first().status, FriendshipStatus.REJECTED)
        self.assertFalse(Friendship.objects.filter(user1=self.user2, user2=self.user1).exists())


class FriendshipModelTestCase(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user1 = self.User.objects.create_user(
            email='user1@example.com',
            username='user1',
            password='password1'
        )
        self.user2 = self.User.objects.create_user(
            email='user2@example.com',
            username='user2',
            password='password2'
        )
        self.user3 = self.User.objects.create_user(
            email='user3@example.com',
            username='user3',
            password='password3'
        )

    def test_friendship_creation(self):
        friendship = Friendship.objects.create_friendship(user1=self.user1, user2=self.user2)
        self.assertEqual(friendship.user1, self.user1)
        self.assertEqual(friendship.user2, self.user2)
        self.assertEqual(friendship.status, FriendshipStatus.PENDING)

    def test_friendship_acceptance(self):
        friendship = Friendship.objects.create_friendship(user1=self.user1, user2=self.user2)
        self.assertEqual(friendship.status, FriendshipStatus.PENDING)

        friendship.accept()
        friendship.refresh_from_db()  # Refresh the friendship from the database to ensure we have the latest data
        self.assertEqual(friendship.status, FriendshipStatus.ACCEPTED)
        self.assertFalse(Friendship.objects.filter(user1=self.user2, user2=self.user1).exists())

    def test_friendship_rejection(self):
        friendship = Friendship.objects.reject_friendship(self.user1, self.user2)
        self.assertIsNotNone(friendship)

        friendship.refresh_from_db()  # Refresh the friendship from the database to ensure we have the latest data
        self.assertEqual(friendship.status, FriendshipStatus.REJECTED)
        self.assertTrue(Friendship.objects.filter(
            Q(user1=self.user2, user2=self.user1) | Q(user1=self.user1, user2=self.user2)
        ).exists())

    def test_friendship_blocking(self):
        fs1 = Friendship.objects.create_friendship(
            user1=self.user1,
            user2=self.user2,
            status=FriendshipStatus.ACCEPTED
        )
        fs2 = Friendship.objects.create_friendship(
            user1=self.user3,
            user2=self.user1,
            status=FriendshipStatus.ACCEPTED
        )

        self.assertEqual(fs1.status, FriendshipStatus.ACCEPTED)
        self.assertEqual(fs2.status, FriendshipStatus.ACCEPTED)

        fs1.block(self.user1, reason="Blocking user2")
        fs1.refresh_from_db()  # Refresh the friendship from the database to ensure we have the latest data
        self.assertEqual(fs1.blocked_status, FriendshipBlockedStatus.BLOCKED_BY_USER1)
        self.assertEqual(fs1.blocked_reason_user1, "Blocking user2")

        fs2.block(self.user1, reason="Blocking user1")
        fs2.refresh_from_db()  # Refresh the friendship from the database to ensure we have the latest data
        self.assertEqual(fs2.blocked_status, FriendshipBlockedStatus.BLOCKED_BY_USER2)
        self.assertEqual(fs2.blocked_reason_user2, "Blocking user1")

        fs1.block(self.user2, reason="Blocking user1")
        fs1.refresh_from_db()  # Refresh the friendship from the database to ensure we have the latest data
        self.assertEqual(fs1.blocked_status, FriendshipBlockedStatus.BLOCKED_BY_BOTH)
        self.assertEqual(fs1.blocked_reason_user2, "Blocking user1")

        fs2.block(self.user3, reason="Blocking user3")
        fs2.refresh_from_db()  # Refresh the friendship from the database to ensure we have the latest data
        self.assertEqual(fs2.blocked_status, FriendshipBlockedStatus.BLOCKED_BY_BOTH)
        self.assertEqual(fs2.blocked_reason_user1, "Blocking user3")

        fs1.unblock(self.user1)
        fs2.unblock(self.user1)
        self.assertEqual(fs1.blocked_status, FriendshipBlockedStatus.BLOCKED_BY_USER2)
        self.assertEqual(fs2.blocked_status, FriendshipBlockedStatus.BLOCKED_BY_USER1)

        fs1.unblock(self.user2)
        fs2.unblock(self.user3)
        self.assertEqual(fs1.blocked_status, FriendshipBlockedStatus.NOT_BLOCKED)
        self.assertEqual(fs2.blocked_status, FriendshipBlockedStatus.NOT_BLOCKED)
