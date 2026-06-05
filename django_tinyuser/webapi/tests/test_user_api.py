"""
Tests for the tinyuser API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('tinyuser.webapi:user-create')
TOKEN_URL = reverse('tinyuser.webapi:token')
ME_URL = reverse('tinyuser.webapi:me')


def create_user(**params):
    """Helper function to create a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Tests the public features of the tinyuser user API."""

    def setUp(self):
        self.client = APIClient()
        self.user_model = get_user_model()

    def test_create_user_success(self):
        """Test creating a user is successful."""

        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'username': 'TestUser',
        }
        res = self.client.post(CREATE_USER_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', res.data)

        user = get_user_model().objects.get(email=payload['email'])

        self.assertTrue(user.check_password(payload['password']))

    def test_create_user_with_existing_email_error(self):
        """Test creating a user with an existing email fails."""

        payload1 = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'username': 'TestUser',
        }
        payload2 = {
            'email': 'test@example.com',
            'password': 'testpass456',
            'username': 'AnotherUser',
        }

        create_user(**payload1)
        res = self.client.post(CREATE_USER_URL, payload2)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_existing_username_error(self):
        """Test creating a user with an existing username fails."""

        payload1 = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'username': 'TestUser',
        }
        payload2 = {
            'email': 'test2@example.com',
            'password': 'testpass456',
            'username': 'TestUser',
        }

        create_user(**payload1)
        res = self.client.post(CREATE_USER_URL, payload2)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_short_password_error(self):
        """Test creating a user with a short password fails."""

        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'username': 'TestUser',
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        email_exists = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(email_exists)

    def test_create_user_with_missing_fields_error(self):
        """Test creating a user with missing fields fails."""

        payload1 = {
            'email': 'test@xeample.com',
            'password': 'testpass123',
        }
        payload2 = {
            'username': 'TestUser',
            'password': 'testpass123',
        }
        res1 = self.client.post(CREATE_USER_URL, payload1)
        res2 = self.client.post(CREATE_USER_URL, payload2)

        self.assertEqual(res1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_invalid_email_error(self):
        """Test creating a user with an invalid email fails."""

        payload = {
            'email': 'invalid-email',
            'password': 'testpass123',
            'username': 'TestUser',
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authentication_required_for_me_endpoint(self):
        """Test that authentication is required for the me endpoint."""

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Tests the private features of the tinyuser user API."""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            username='TestUser',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_profile_success(self):
        """Test retrieving profile for logged in user."""

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['email'], self.user.email)
        self.assertEqual(res.data['username'], self.user.username)
        self.assertNotIn('password', res.data)

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me endpoint."""

        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_user_profile_success(self):
        """Test updating the user profile for authenticated user."""

        payload = {
            'password': 'newPassword123',
            'username': 'NewUsername',
        }

        res = self.client.patch(ME_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, payload['username'])
        self.assertTrue(self.user.check_password(payload['password']))

        self.assertEqual(res.data['email'], self.user.email)
        self.assertEqual(res.data['username'], self.user.username)
        self.assertNotIn('password', res.data)

    def test_patch_user_update_email_not_allowed(self):
        """Test that updating the email is not allowed."""

        payload = {
            'email': 'new.email@example.com'
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_patch_user_update_username_allowed(self):
        """Test that updating the username is allowed."""

        payload = {
            'username': 'NewUsername'
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['username'], 'NewUsername')


class TokenAPITests(TestCase):
    """Tests for the user authentication token API."""

    def setUp(self):
        self.client = APIClient()
        self.user_model = get_user_model()

    def test_create_token_for_user_valid_credentials(self):
        """Test that a token is created for the user with valid credentials."""

        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
        }
        create_user(email=payload['email'], password=payload['password'], username='TestUser')
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_for_user_invalid_credentials(self):
        """Test that a token is not created if invalid credentials are given."""

        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
        }
        create_user(email=payload['email'], password=payload['password'], username='TestUser')

        payload['password'] = 'wrongpass'
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        payload['email'] = 'nonexistent@example.com'
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_user_missing_fields(self):
        """Test that email and password are required to create a token."""

        user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'username': 'TestUser',
        }
        create_user(**user_data)

        res = self.client.post(TOKEN_URL, {'email': '', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        res = self.client.post(TOKEN_URL, {'email': user_data['email'], 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        res = self.client.post(TOKEN_URL, {'email': '', 'password': user_data['password']})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        res = self.client.post(TOKEN_URL, {'password': user_data['password']})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        res = self.client.post(TOKEN_URL, {'email': user_data['email']})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        res = self.client.post(TOKEN_URL, {})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
