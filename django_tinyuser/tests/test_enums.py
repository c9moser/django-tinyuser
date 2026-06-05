from django.test import TestCase
from django_tinyuser.enums import (
    FriendshipStatus,
    FriendshipBlockedStatus,
)


class FriendshipStatusEnumTestCase(TestCase):
    def test_from_string_valid(self):
        self.assertEqual(FriendshipStatus.from_string('pending'), FriendshipStatus.PENDING)
        self.assertEqual(FriendshipStatus.from_string('accepted'), FriendshipStatus.ACCEPTED)
        self.assertEqual(FriendshipStatus.from_string('rejected'), FriendshipStatus.REJECTED)

    def test_from_string_invalid(self):
        with self.assertRaises(ValueError):
            FriendshipStatus.from_string('invalid_status')

    def test_name_raw(self):
        self.assertEqual(FriendshipStatus.PENDING.name_raw, 'pending')
        self.assertEqual(FriendshipStatus.ACCEPTED.name_raw, 'accepted')
        self.assertEqual(FriendshipStatus.REJECTED.name_raw, 'rejected')

    def test_str_and_repr(self):
        self.assertEqual(str(FriendshipStatus.PENDING), 'pending')
        self.assertEqual(repr(FriendshipStatus.PENDING), '<FriendshipStatus.PENDING>')
        self.assertEqual(str(FriendshipStatus.ACCEPTED), 'accepted')
        self.assertEqual(repr(FriendshipStatus.ACCEPTED), '<FriendshipStatus.ACCEPTED>')
        self.assertEqual(str(FriendshipStatus.REJECTED), 'rejected')
        self.assertEqual(repr(FriendshipStatus.REJECTED), '<FriendshipStatus.REJECTED>')


class FriendshipBlockedStatusEnumTestCase(TestCase):
    def test_from_string_valid(self):
        self.assertEqual(FriendshipBlockedStatus.from_string('not_blocked'),
                         FriendshipBlockedStatus.NOT_BLOCKED)
        self.assertEqual(FriendshipBlockedStatus.from_string('blocked_by_user1'),
                         FriendshipBlockedStatus.BLOCKED_BY_USER1)
        self.assertEqual(FriendshipBlockedStatus.from_string('blocked_by_user2'),
                         FriendshipBlockedStatus.BLOCKED_BY_USER2)
        self.assertEqual(FriendshipBlockedStatus.from_string('blocked_by_both'),
                         FriendshipBlockedStatus.BLOCKED_BY_BOTH)

    def test_from_string_invalid(self):
        with self.assertRaises(ValueError):
            FriendshipBlockedStatus.from_string('invalid_status')

    def test_name_raw(self):
        self.assertEqual(FriendshipBlockedStatus.NOT_BLOCKED.name_raw, 'not blocked')
        self.assertEqual(FriendshipBlockedStatus.BLOCKED_BY_USER1.name_raw, 'blocked by user1')
        self.assertEqual(FriendshipBlockedStatus.BLOCKED_BY_USER2.name_raw, 'blocked by user2')
        self.assertEqual(FriendshipBlockedStatus.BLOCKED_BY_BOTH.name_raw, 'blocked by both users')

    def test_str_and_repr(self):
        self.assertEqual(str(FriendshipBlockedStatus.NOT_BLOCKED),
                         'not_blocked')
        self.assertEqual(repr(FriendshipBlockedStatus.NOT_BLOCKED),
                         '<FriendshipBlockedStatus.NOT_BLOCKED>')
        self.assertEqual(str(FriendshipBlockedStatus.BLOCKED_BY_USER1),
                         'blocked_by_user1')
        self.assertEqual(repr(FriendshipBlockedStatus.BLOCKED_BY_USER1),
                         '<FriendshipBlockedStatus.BLOCKED_BY_USER1>')
        self.assertEqual(str(FriendshipBlockedStatus.BLOCKED_BY_USER2),
                         'blocked_by_user2')
        self.assertEqual(repr(FriendshipBlockedStatus.BLOCKED_BY_USER2),
                         '<FriendshipBlockedStatus.BLOCKED_BY_USER2>')
        self.assertEqual(str(FriendshipBlockedStatus.BLOCKED_BY_BOTH),
                         'blocked_by_both')
        self.assertEqual(repr(FriendshipBlockedStatus.BLOCKED_BY_BOTH),
                         '<FriendshipBlockedStatus.BLOCKED_BY_BOTH>')
