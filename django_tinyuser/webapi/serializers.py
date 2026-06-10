"""Serializers for the user API Views."""

from allauth.account.adapter import get_adapter
from django.contrib.auth import (
    authenticate,
    get_user_model,
)
from django.db.utils import IntegrityError
from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError

from django_tinyuser.models import TinyUserProfile as UserProfile


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for the TinyUserProfile model."""

    class Meta:
        model = UserProfile
        fields = [
            "first_name",
            "last_name",
            "bio",
            "location",
            "website",
            "birth_date",
            "avatar_small",
            "avatar_medium",
            "avatar_large",
            "avatar_full",
        ]
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
            "location": {"required": False},
            "website": {"required": False},
            "birth_date": {"required": False},
            "bio": {"required": False},
            "avatar_small": {"required": False},
            "avatar_medium": {"required": False},
            "avatar_large": {"required": False},
            "avatar_full": {"required": False},
        }


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ("email", "password", "username")
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 8},
        }

    def create(self, validated_data):
        """Create a new user with encrypted password and return it."""

        if not validated_data.get("email"):
            raise serializers.ValidationError(_("Email is required."))
        if not validated_data.get("username"):
            raise serializers.ValidationError(_("Username is required."))
        if not validated_data.get("password"):
            raise serializers.ValidationError(_("Password is required."))

        if not get_adapter().is_open_for_signup(self.context["request"]):
            raise PermissionDenied(_("Signups are not allowed."))

        user = get_user_model().objects.create_user(**validated_data)

        return user

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it."""
        password = validated_data.pop("password", None)

        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class SafeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        profile = ProfileSerializer(required=False)
        fields = ("email", "username", "password", "profile")
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 8},
            "email": {"read_only": True},
        }

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it."""

        password = validated_data.pop("password", None)

        if "email" in validated_data:
            raise serializers.ValidationError(_("Email cannot be updated."))

        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)

        user.save()

        # refresh user from database
        user.refresh_from_db()

        return user


class UserProfileSerializer(serializers.Serializer):
    """Serializer for the user profile object."""

    profile = ProfileSerializer(required=False)

    class Meta:
        model = UserProfile
        fields = ["email", "username", "profile", "password"]
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 8},
            "email": {"read_only": True},
        }

    def update(self, instance, validated_data):
        """Update user profile."""
        profile_data = validated_data.pop("profile", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object."""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password,
        )
        if not user:
            msg = _("Unable to authenticate with provided credentials.")
            raise serializers.ValidationError(msg, code="authentication")

        attrs["user"] = user
        return attrs


class InvitationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        from invitations.utils import get_invitation_model

        if not validated_data.get("email"):
            raise serializers.ValidationError("email is required")

        if not getattr(self.context.get("request"), "user", None):
            raise serializers.ValidationError("inviter is required")

        email = validated_data.get("email")
        try:
            invitation = get_invitation_model().create(
                email=email, inviter=self.context.get("request").user
            )
        except IntegrityError:
            raise ValidationError("email already exists")
        invitation.send_invitation(self.context.get("request"))
        return invitation
