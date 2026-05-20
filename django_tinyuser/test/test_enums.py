from django.test import TestCase
from django_tinyuser.enums import FriendshipStatus

class FriendshipStatusEnumTestCase(TestCase):
    def test_from_string_valid(self):
        self.assertEqual(FriendshipStatus.from_string('pending'), FriendshipStatus.PENDING)
        self.assertEqual(FriendshipStatus.from_string('accepted'), FriendshipStatus.ACCEPTED)
        self.assertEqual(FriendshipStatus.from_string('rejected'), FriendshipStatus.REJECTED)
        self.assertEqual(FriendshipStatus.from_string('blocked'), FriendshipStatus.BLOCKED)

    def test_from_string_invalid(self):
        with self.assertRaises(ValueError):
            FriendshipStatus.from_string('invalid_status')

    def test_name_raw(self):
        self.assertEqual(FriendshipStatus.PENDING.name_raw, 'pending')
        self.assertEqual(FriendshipStatus.ACCEPTED.name_raw, 'accepted')
        self.assertEqual(FriendshipStatus.REJECTED.name_raw, 'rejected')
        self.assertEqual(FriendshipStatus.BLOCKED.name_raw, 'blocked')

    def test_str_and_repr(self):
        self.assertEqual(str(FriendshipStatus.PENDING), 'pending')
        self.assertEqual(repr(FriendshipStatus.PENDING), '<FriendshipStatus: PENDING>')
        self.assertEqual(str(FriendshipStatus.ACCEPTED), 'accepted')
        self.assertEqual(repr(FriendshipStatus.ACCEPTED), '<FriendshipStatus: ACCEPTED>')
        self.assertEqual(str(FriendshipStatus.REJECTED), 'rejected')
        self.assertEqual(repr(FriendshipStatus.REJECTED), '<FriendshipStatus: REJECTED>')
        self.assertEqual(str(FriendshipStatus.BLOCKED), 'blocked')
        self.assertEqual(repr(FriendshipStatus.BLOCKED), '<FriendshipStatus: BLOCKED>')
