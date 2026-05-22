from django.test import TestCase
from django_tinyuser.enums import (
    FriendshipStatus,
    FriendshipBlockedStatus,
)
from django_tinyuser.models import (
    TinyUser,
    TinyUserProfile,
    UserFriendship,
    UserFriendGroup,
)


class TinyUserModelTestCase(TestCase):
    def test_create_user(self):
        user = TinyUser.objects.create_user(username='testuser',
                                            email='testuser@example.com',
                                            password='testpassword')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'testuser@example.com')

    def create_superuser(self):
        superuser = TinyUser.objects.create_superuser(username='admin',
                                                      email='admin@example.com',
                                                      password='adminpassword')
        self.assertEqual(superuser.username, 'admin')
        self.assertEqual(superuser.email, 'admin@example.com')
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

        self.assertRaises(
            ValueError,
            TinyUser.objects.create_superuser(
                username='admin2',
                email='admin2@example.com',
                password='admin2password',
                is_superuser=False
            )
        )
        self.assertRaises(
            ValueError,
            TinyUser.objects.create_superuser(
                username='admin2',
                email='admin2@example.com',
                password='admin2password',
                is_staff=False
            )
        )

    def test_create_tiny_user_profile(self):
        user = TinyUser.objects.create_user(username='testuser',
                                            email='testuser@example.com',
                                            password='testpassword')
        profile = TinyUserProfile.objects.create(user=user,
                                                 first_name='Test',
                                                 last_name='User',
                                                 bio='This is a test bio.')
        self.assertEqual(profile.user, user)
        self.assertEqual(profile.first_name, 'Test')
        self.assertEqual(profile.last_name, 'User')
        self.assertEqual(profile.bio, 'This is a test bio.')


class UserFriendshipModelTestCase(TestCase):
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

    def test_create_friendship(self):
        friendship = UserFriendship.objects.create(from_user=self.user1, to_user=self.user2)
        self.assertEqual(friendship.from_user, self.user1)
        self.assertEqual(friendship.to_user, self.user2)
        self.assertEqual(friendship.status, FriendshipStatus.PENDING)
        self.assertEqual(friendship.blocked_status, FriendshipBlockedStatus.NOT_BLOCKED)
        self.assertEqual(UserFriendship.objects.filter(from_user=self.user1, to_user=self.user2).count(), 1)

    def test_accept_friendship(self):
        friendship1 = UserFriendship.objects.create(from_user=self.user1, to_user=self.user2, is_initiator=True)
        friendship2 = UserFriendship.objects.create(from_user=self.user2, to_user=self.user1)
        self.assertEqual(friendship1.status, FriendshipStatus.PENDING)
        self.assertEqual(friendship2.status, FriendshipStatus.PENDING)

        # Cannot accept a friendship where we are the initiator
        self.assertRaises(ValueError, friendship1.accept)

        friendship2.accept()
        friendship1.refresh_from_db()
        friendship2.refresh_from_db()

        self.assertEqual(friendship1.status, FriendshipStatus.ACCEPTED)
        self.assertEqual(friendship1.blocked_status, FriendshipBlockedStatus.NOT_BLOCKED)
        self.assertEqual(friendship2.status, FriendshipStatus.ACCEPTED)
        self.assertEqual(friendship2.blocked_status, FriendshipBlockedStatus.NOT_BLOCKED)

    def test_reject_friendship(self):
        friendship1 = UserFriendship.objects.create(from_user=self.user1, to_user=self.user2)
        friendship1.reject()
        self.assertEqual(friendship1.status, FriendshipStatus.REJECTED)

        friendship2 = UserFriendship.objects.get(from_user=self.user2, to_user=self.user1)
        self.assertEqual(friendship2.status, FriendshipStatus.REJECTED)
        self.assertEqual(friendship2.blocked_status, FriendshipBlockedStatus.NOT_BLOCKED)

    def test_block_friendship_from_user(self):
        friendship1 = UserFriendship.objects.create(from_user=self.user1, to_user=self.user2, is_initiator=True)
        friendship2 = UserFriendship.objects.create(from_user=self.user2, to_user=self.user1)
        friendship2.accept()  # Accept the friendship first to ensure it's in an accepted state before blocking

        friendship1.block()

        friendship1.refresh_from_db()
        friendship2.refresh_from_db()

        self.assertEqual(friendship1.blocked_status, FriendshipBlockedStatus.BLOCKED_BY_FROM_USER)
        self.assertEqual(friendship2.blocked_status, FriendshipBlockedStatus.BLOCKED_BY_TO_USER)

    def test_block_friendship_to_user(self):
        friendship1 = UserFriendship.objects.create(from_user=self.user1, to_user=self.user2, is_initiator=True)
        friendship2 = UserFriendship.objects.create(from_user=self.user2, to_user=self.user1)
        friendship2.accept()  # Accept the friendship first to ensure it's in an accepted state before blocking

        friendship2.block()

        friendship1.refresh_from_db()
        friendship2.refresh_from_db()

        self.assertEqual(friendship1.blocked_status, FriendshipBlockedStatus.BLOCKED_BY_TO_USER)
        self.assertEqual(friendship2.blocked_status, FriendshipBlockedStatus.BLOCKED_BY_FROM_USER)


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
