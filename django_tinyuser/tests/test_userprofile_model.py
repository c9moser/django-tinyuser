from random import seed
from sqlite3.dbapi2 import Time

from django.conf import settings as django_settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from django_tinyuser.models import TinyUserProfile
from django_tinyuser.models.tinyuser import TinyUser


class TestUserProfileModel(TestCase):
    PROFILE_DATA = {
        "bio": "Test bio",
        "first_name": "FirstName",
        "last_name": "LastName",
        "location": "Vienna",
        "website": "https://example.com",
        "birth_date": "1970-1-1",
    }

    def setUp(self):
        import os
        import urllib
        from uuid import uuid4

        import PIL

        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )
        self.temp_dir = f"/tmp/{uuid4()}"
        self.media_root = f"{self.temp_dir}/media"
        self.images_dir = f"{self.temp_dir}/images"
        os.makedirs(self.media_root)
        os.makedirs(self.images_dir)

        django_settings.MEDIA_ROOT = self.media_root

    def tearDown(self):
        import os

        if os.path.exists(self.temp_dir):
            for root, dirs, files in os.walk(self.temp_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self.temp_dir)

    def test_user_profile_creation(self):
        self.assertIsNotNone(self.user)

        profile = TinyUserProfile.objects.create(user=self.user, **self.PROFILE_DATA)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.bio, "Test bio")
        self.assertEqual(profile.first_name, "FirstName")
        self.assertEqual(profile.last_name, "LastName")
        self.assertEqual(profile.website, "https://example.com")
        self.assertEqual(profile.birth_date, "1970-1-1")
        self.assertEqual(profile.location, "Vienna")
        self.assertEqual(str(profile), f"{self.user.username}'s profile")

    def test_user_profile_update(self):
        TinyUserProfile.objects.create(user=self.user, **self.PROFILE_DATA)

        self.user.profile.bio = "Test updated bio"
        self.user.profile.first_name = "UpdatedFirstName"
        self.user.profile.last_name = "UpdatedLastName"
        self.user.profile.website = "https://updated.example.com"
        self.user.profile.birth_date = "1971-1-1"
        self.user.profile.location = "Graz"
        self.user.profile.save()
        self.assertEqual(self.user.profile.bio, "Test updated bio")
        self.assertEqual(self.user.profile.first_name, "UpdatedFirstName")
        self.assertEqual(self.user.profile.last_name, "UpdatedLastName")
        self.assertEqual(self.user.profile.website, "https://updated.example.com")
        self.assertEqual(self.user.profile.birth_date, "1971-1-1")
        self.assertEqual(self.user.profile.location, "Graz")
