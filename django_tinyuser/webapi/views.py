"""Views for the user API."""

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from .serializers import (
    # UserProfileSerializer,
    SafeUserSerializer,
    UserSerializer,
    AuthTokenSerializer,
)
# from django.contrib.auth import get_user_model


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""

    #: serializer_class: The serializer class to use for validating
    #: and deserializing input, and for serializing output.
    serializer_class = UserSerializer

    #: authentication_classes: The authentication classes to use for
    #: this view. In this case, no authentication is required to create a user.
    permission_classes = (permissions.AllowAny,)


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    """Manage the authenticated user."""
    serializer_class = SafeUserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
