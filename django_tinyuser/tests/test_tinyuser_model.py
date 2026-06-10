from django.test import TestCase
from django_tinyuser.models import (
    TinyUser,
    TinyUserProfile,
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
