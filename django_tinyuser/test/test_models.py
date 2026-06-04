from django.test import TestCase
from django_tinyuser.enums import (
    FriendshipStatus,
    FriendshipBlockedStatus,
)
from django_tinyuser.models import (
    Friendship,
    FriendGroup,
)


class FriendshipModelTestCase(TestCase):
    """
    Test case for the Friendship model.
    """
    def setUp(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()

        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password1'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password2'
        )
        self.user3 = User.objects.create_user(
            username='user3',
            email='user3@example.com',
            password='password3'
        )
        self.user4 = User.objects.create_user(
            username='user4',
            email='user4@example.com',
            password='password4'
        )

        self.friendship.objects.create(user1=self.user1, user2=self.user2, user1_is_initiator=True)
        self.user2.friendship.objects.create(user1=self.user2, user2=self.user1)
        f1.friendship_status = FriendshipStatus.ACCEPTED
        f1.save()

        f1 = self.user1.friendship.objects.create(user1=self.user1, user2=self.user3, user1_is_initiator=True)
        f1.friendship_status = FriendshipStatus.REJECTED
        f1.save()

        self.user3.friendship.objects.create(user1=self.user2, user2=self.user3, user1_is_initiator=False)

    def test_create_friendship(self):
        friendship = Friendship.objects.create(user1=self.user1, user2=self.user4)
        self.assertEqual(friendship.user1, self.user1)
        self.assertEqual(friendship.status, FriendshipStatus.PENDING)
        self.assertEqual(friendship.blocked_status, FriendshipBlockedStatus.NOT_BLOCKED)
        self.assertEqual(Friendship.objects.filter(user1=self.user1, user2=self.user4).count(), 1)

    def test_accept_friendship(self):
        # Cannot accept a friendship where we are the initiator
        pending_friendship_count = self.user1.friendship.filter(
            status=FriendshipStatus.PENDING,
            is_initiator=True
        ).count()
        accepted_friendship_count = self.user1.friendship.filter(status=FriendshipStatus.ACCEPTED).count()
        rejected_friendship_count = self.user1.friendship.filter(status=FriendshipStatus.REJECTED).count()

        self.assertEqual(pending_friendship_count, 2)
        friendship = self.user1.friendship.filter(status=FriendshipStatus.PENDING, user1_is_initiator=True).first()
        self.assertIsNotNone(friendship)
        self.assertEqual(
            (pending_friendship_count - 1),
            friendship.user1.friendship.filter(status=FriendshipStatus.PENDING, user1_is_initiator=True).count()
        )
        self.assertEqual(
            (accepted_friendship_count + 1),
            friendship.user1.friendship.filter(status=FriendshipStatus.ACCEPTED).count()
        )
        self.assertEqual(
            rejected_friendship_count,
            friendship.user1.friendship.filter(status=FriendshipStatus.REJECTED).count()
        )
        self.assertEqual(friendship.status, FriendshipStatus.ACCEPTED)

    def test_reject_friendship(self):
        friendship = self.user1.friendship.filter(status=FriendshipStatus.PENDING, is_initiator=True).first()

        self.assertIsNotNone(friendship)
        friendship.reject()
        self.assertEqual(friendship.status, FriendshipStatus.REJECTED)

        friendship = Friendship.objects.get(user1=self.user2, user2=self.user1)
        self.assertEqual(friendship.status, FriendshipStatus.REJECTED)
        self.assertEqual(friendship.blocked_status, FriendshipBlockedStatus.NOT_BLOCKED)

    def test_friendship_block_unblock(self):

        friendship1 = Friendship.objects.filter(user1=self.user1, user2=self.user2, status=FriendshipStatus.ACCEPTED)[0]
        friendship2 = Friendship.objects.filter(user1=self.user2, user2=self.user1, status=FriendshipStatus.PENDING)[0]
        friendship2.accept()

        friendship2.refresh_from_db()

        self.assertEqual(friendship1.status, FriendshipStatus.ACCEPTED)
        self.assertEqual(friendship2.status, FriendshipStatus.ACCEPTED)
        self.assertEqual(friendship1.blocked_status, FriendshipBlockedStatus.NOT_BLOCKED)
        self.assertEqual(friendship2.blocked_status, FriendshipBlockedStatus.NOT_BLOCKED)

        friendship1.block(user=friendship1.user1)
        friendship2.block(user=friendship2.user2)
        friendship1.refresh_from_db()
        friendship2.refresh_from_db()
        self.assertEqual(friendship1.blocked_status, FriendshipBlockedStatus.BLOCKED_BY_USER1)
        self.assertEqual(friendship2.blocked_status, FriendshipBlockedStatus.BLOCKED_BY_USER2)

        friendship1.block(user=friendship1.user1)
        friendship2.block(user=friendship2.user2)
        friendship1.refresh_from_db()
        friendship2.refresh_from_db()
        self.assertEqual(friendship1.blocked_status, FriendshipBlockedStatus.BLOCKED_BY_USER1)
        self.assertEqual(friendship2.blocked_status, FriendshipBlockedStatus.BLOCKED_BY_USER2)

        friendship1.block(user=friendship1.user2)
        friendship2.block(user=friendship2.user1)
        friendship1.refresh_from_db()
        friendship2.refresh_from_db()
        self.assertEqual(friendship1.blocked_status, FriendshipBlockedStatus.BLOCKED_BY_BOTH)
        self.assertEqual(friendship2.blocked_status, FriendshipBlockedStatus.BLOCKED_BY_BOTH)

        friendship1.unblock(user=friendship1.user2)
        friendship2.unblock(user=friendship2.user1)
        friendship1.refresh_from_db()
        friendship2.refresh_from_db()
        self.assertEqual(friendship1.blocked_status, FriendshipBlockedStatus.BLOCKED_BY_USER1)
        self.assertEqual(friendship2.blocked_status, FriendshipBlockedStatus.BLOCKED_BY_USER2)

        friendship1.unblock(user=friendship1.user2)
        friendship2.unblock(user=friendship2.user1)
        friendship1.refresh_from_db()
        friendship2.refresh_from_db()
        self.assertEqual(friendship1.blocked_status, FriendshipBlockedStatus.BLOCKED_BY_USER1)
        self.assertEqual(friendship2.blocked_status, FriendshipBlockedStatus.BLOCKED_BY_USER2)

        friendship1.unblock(user=friendship1.user1)
        friendship2.unblock(user=friendship2.user2)
        friendship1.refresh_from_db()
        friendship2.refresh_from_db()
        self.assertEqual(friendship1.blocked_status, FriendshipBlockedStatus.NOT_BLOCKED)
        self.assertEqual(friendship2.blocked_status, FriendshipBlockedStatus.NOT_BLOCKED)


class UserFriendGroupModelTestCase(TestCase):

    def setUp(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()

        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password1'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password2'
        )

    def test_create_friend_group(self):
        group = UserFriendGroup.objects.create(name='Test Group', user=self.user1)
        group.members.add(self.user2)
        self.assertEqual(group.name, 'Test Group')
        self.assertEqual(group.user, self.user1)
        self.assertIn(self.user2, group.members.all())

        self.assertEqual(UserFriendGroup.objects.filter(name='Test Group', user=self.user1).count(), 1)
