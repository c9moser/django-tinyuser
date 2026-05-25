"""Views for the user API."""

from rest_framework import generics, permissions
from .serializers import UserSerializer

from rest_framework import status
from rest_framework.response import Response


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        """Override create method to return custom response."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'email': user.email,
                'username': user.username,
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer):
        """Create and return the new user."""
        return serializer.save()
