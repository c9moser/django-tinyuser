from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from django_tinyuser.models import UserProfile


class TestUserProfileModel(TestCase):
    PROFILE_DATA = {
        "bio": "Test bio",
        "first_name": "FirstName",
        "last_name": "LastName",
        "location": "Vienna",
        "website": "https://example.com",
        "birth_date": date(1970, 1, 1),
    }

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )

    def test_user_profile_creation(self):
        self.assertIsNotNone(self.user)

        profile = UserProfile.objects.create(user=self.user, **self.PROFILE_DATA)
        profile.refresh_from_db()
        self.assertIsNotNone(profile)
        self.assertEqual(profile.bio, "Test bio")
        self.assertEqual(profile.first_name, "FirstName")
        self.assertEqual(profile.last_name, "LastName")
        self.assertEqual(profile.website, "https://example.com")
        self.assertEqual(profile.birth_date, date(1970, 1, 1))
        self.assertEqual(profile.location, "Vienna")
        self.assertEqual(str(profile), f"{self.user.username}'s profile")

    def test_user_profile_update(self):
        UserProfile.objects.create(user=self.user, **self.PROFILE_DATA)

        self.user.tinyuser_profile.bio = "Test updated bio"
        self.user.tinyuser_profile.first_name = "UpdatedFirstName"
        self.user.tinyuser_profile.last_name = "UpdatedLastName"
        self.user.tinyuser_profile.website = "https://updated.example.com"
        self.user.tinyuser_profile.birth_date = date(1971, 1, 1)
        self.user.tinyuser_profile.location = "Berlin"
        self.user.tinyuser_profile.save()
        self.user.tinyuser_profile.refresh_from_db()
        self.assertEqual(self.user.tinyuser_profile.bio, "Test updated bio")
        self.assertEqual(self.user.tinyuser_profile.first_name, "UpdatedFirstName")
        self.assertEqual(self.user.tinyuser_profile.last_name, "UpdatedLastName")
        self.assertEqual(
            self.user.tinyuser_profile.website, "https://updated.example.com"
        )
        self.assertEqual(self.user.tinyuser_profile.birth_date.year, 1971)
        self.assertEqual(self.user.tinyuser_profile.birth_date.month, 1)
        self.assertEqual(self.user.tinyuser_profile.birth_date.day, 1)
        self.assertEqual(self.user.tinyuser_profile.location, "Berlin")
