from django.conf import settings as django_settings
from django.contrib.auth.models import Group
from django.core import mail as django_mail
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from django_tinyuser import settings
from django_tinyuser.models import TinyUser

URL_INVITE = reverse("tinyuser.webapi:invite")


class TestInvitationPrivateAPI(TestCase):
    def setUp(self):
        self.standard_user = TinyUser.objects.create_user(
            email="std_test@example.com",
            username="testuser",
            password="testpass123",
        )
        self.invitor_user = TinyUser.objects.create_user(
            email="invitor@example.com",
            username="invitor",
            password="invitorpass123",
        )
        self.group_invitors = Group.objects.get_or_create(name="invitors")[0]
        self.invitor_user.groups.add(self.group_invitors)
        self.superuser = TinyUser.objects.create_superuser(
            email="superuser@example.com",
            username="superuser",
            password="superuserpass123",
        )

        django_settings.DEFAULT_FROM_EMAIL = "testing.invitations@example.com"
        django_settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

        self.client = APIClient()

    def test_invite_unauthenticated_failed(self):
        """Test that an unauthenticated user cannot invite others."""
        n_messages = len(getattr(django_mail, "outbox", []))
        settings.INVITE_ALLOW_ALL_AUTHENTICATED_USERS = True
        settings.INVITE_GROUPS = []

        self.client.force_authenticate(user=None)

        response = self.client.post(URL_INVITE, data={"email": "invitee@example.com"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(django_mail.outbox), n_messages)

    def test_invite_allowed_all_success(self):
        """Test that an authenticated user can invite others when allowed by settings."""
        settings.INVITE_ALLOW_ALL_AUTHENTICATED_USERS = True
        self.client.force_authenticate(user=self.standard_user)
        n_messages = len(getattr(django_mail, "outbox", []))
        response = self.client.post(URL_INVITE, data={"email": "invitee@example.com"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(django_mail.outbox), n_messages + 1)

    def test_invite_not_allowed_all_failed(self):
        """Test that an authenticated user cannot invite others when not allowed by settings."""
        settings.INVITE_ALLOW_ALL_AUTHENTICATED_USERS = False
        self.client.force_authenticate(user=self.standard_user)
        n_messages = len(getattr(django_mail, "outbox", []))
        response = self.client.post(URL_INVITE, data={"email": "invitee@example.com"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(django_mail.outbox), n_messages)

    def test_invite_double_invite_failed(self):
        """Test that an authenticated user cannot invite the same email twice."""
        self.client.force_authenticate(user=self.superuser)
        n_messages = len(getattr(django_mail, "outbox", []))
        response = self.client.post(URL_INVITE, data={"email": "invitee@example.com"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(django_mail.outbox), n_messages + 1)
        response = self.client.post(URL_INVITE, data={"email": "invitee@example.com"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(django_mail.outbox), n_messages + 1)

    def test_invite_allowed_group_success(self):
        """Test that an authenticated user can invite others when allowed by settings."""
        settings.INVITE_ALLOW_ALL_AUTHENTICATED_USERS = False
        settings.INVITE_GROUPS = [self.group_invitors.name]
        self.client.force_authenticate(user=self.invitor_user)
        n_messages = len(getattr(django_mail, "outbox", []))
        response = self.client.post(URL_INVITE, data={"email": "invitee@example.com"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(django_mail.outbox), n_messages + 1)

    def test_invite_allowed_group_failed(self):
        """Test that an authenticated user cannot invite others when not allowed by settings."""
        settings.INVITE_ALLOW_ALL_AUTHENTICATED_USERS = False
        settings.INVITE_GROUPS = ["invitors"]
        self.client.force_authenticate(user=self.standard_user)
        n_messages = len(getattr(django_mail, "outbox", []))
        response = self.client.post(URL_INVITE, data={"email": "invitee@example.com"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(django_mail.outbox), n_messages)

    def test_invite_restricetd_standard_user_failed(self):
        """Test that a restricted standard user cannot invite others."""
        settings.INVITE_ALLOW_ALL_AUTHENTICATED_USERS = False
        settings.INVITE_GROUPS = []
        self.client.force_authenticate(user=self.standard_user)
        n_messages = len(getattr(django_mail, "outbox", []))
        response = self.client.post(URL_INVITE, data={"email": "invitee@example.com"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(django_mail.outbox), n_messages)

    def test_invite_restricted_invitor_failed(self):
        """Test that a restricted standard user cannot invite others."""
        settings.INVITE_ALLOW_ALL_AUTHENTICATED_USERS = False
        settings.INVITE_GROUPS = []
        self.client.force_authenticate(user=self.standard_user)
        n_messages = len(getattr(django_mail, "outbox", []))
        response = self.client.post(URL_INVITE, data={"email": "invitee@example.com"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(django_mail.outbox), n_messages)

    def test_invite_superuser_success(self):
        """Test that a superuser can invite others."""
        settings.INVITE_ALLOW_ALL_AUTHENTICATED_USERS = False
        settings.INVITE_GROUPS = []

        self.client.force_authenticate(user=self.superuser)
        n_messages = len(getattr(django_mail, "outbox", []))
        response = self.client.post(URL_INVITE, data={"email": "invitee@example.com"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(django_mail.outbox), n_messages + 1)

    def test_invite_accepted_invtation_failed(self):
        """Test that an accepted invitation cannot be used to invite others."""

        import re

        settings.INVITE_ALLOW_ALL_AUTHENTICATED_USERS = False
        settings.INVITE_GROUPS = []

        self.client.force_authenticate(user=self.superuser)
        n_messages = len(getattr(django_mail, "outbox", []))
        response = self.client.post(URL_INVITE, data={"email": "invitee@example.com"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(django_mail.outbox), n_messages + 1)

        message: django_mail.EmailMessage = django_mail.outbox[-1]
        self.assertEqual(message.recipients(), ["invitee@example.com"])
        self.assertIn("Invitation to join", message.subject)
        result = re.search(
            r"http://testserver/invitations/accept-invite/.+", message.body
        )
        self.assertTrue(result)

        response_url = re.search(
            r"http://testserver(/invitations/accept-invite/.+)", message.body
        ).group(1)

        response = self.client.get(response_url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        response = self.client.post(response_url)
        self.assertEqual(response.status_code, status.HTTP_410_GONE)
