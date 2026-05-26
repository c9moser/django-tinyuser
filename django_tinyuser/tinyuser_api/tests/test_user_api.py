"""
Tests for the tinyuser API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('tinyuser.api:user-create')
TOKEN_URL = reverse('tinyuser.api:token')


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
        res = self.client.post(CREATE_USER_URL, payload)

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
