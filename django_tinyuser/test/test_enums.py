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
        self.assertEqual(FriendshipBlockedStatus.from_string('blocked_by_from_user'),
                         FriendshipBlockedStatus.BLOCKED_BY_FROM_USER)
        self.assertEqual(FriendshipBlockedStatus.from_string('blocked_by_to_user'),
                         FriendshipBlockedStatus.BLOCKED_BY_TO_USER)

    def test_from_string_invalid(self):
        with self.assertRaises(ValueError):
            FriendshipBlockedStatus.from_string('invalid_status')

    def test_name_raw(self):
        self.assertEqual(FriendshipBlockedStatus.NOT_BLOCKED.name_raw, 'not blocked')
        self.assertEqual(FriendshipBlockedStatus.BLOCKED_BY_FROM_USER.name_raw, 'blocked by from user')
        self.assertEqual(FriendshipBlockedStatus.BLOCKED_BY_TO_USER.name_raw, 'blocked by to user')

    def test_str_and_repr(self):
        self.assertEqual(str(FriendshipBlockedStatus.NOT_BLOCKED),
                         'not_blocked')
        self.assertEqual(repr(FriendshipBlockedStatus.NOT_BLOCKED),
                         '<FriendshipBlockedStatus.NOT_BLOCKED>')
        self.assertEqual(str(FriendshipBlockedStatus.BLOCKED_BY_FROM_USER),
                         'blocked_by_from_user')
        self.assertEqual(repr(FriendshipBlockedStatus.BLOCKED_BY_FROM_USER),
                         '<FriendshipBlockedStatus.BLOCKED_BY_FROM_USER>')
        self.assertEqual(str(FriendshipBlockedStatus.BLOCKED_BY_TO_USER),
                         'blocked_by_to_user')
        self.assertEqual(repr(FriendshipBlockedStatus.BLOCKED_BY_TO_USER),
                         '<FriendshipBlockedStatus.BLOCKED_BY_TO_USER>')
