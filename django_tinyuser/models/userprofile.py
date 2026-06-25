import markdown
from django.conf import settings as django_settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_tinyuser import settings

from .fields import RestrictedImageField


class UserProfile(models.Model):
    """Model to store additional profile information for TinyUser."""

    #: The user field is a one-to-one relationship with the TinyUser model, linking each profile to a specific user.
    #: It is required and will be deleted if the associated user is deleted.
    user = models.OneToOneField(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tinyuser_profile",
    )

    #: The first_name field stores the user's first name.
    #: It is optional and can be left blank.
    first_name = models.CharField(
        max_length=30,
        blank=True,
    )
    #: The last_name field stores the user's last name.
    #: It is optional and can be left blank.
    last_name = models.CharField(max_length=30, blank=True)

    #: The bio field allows users to provide a short biography or description
    #: about themselves. It is optional and can be left blank.
    bio = models.TextField(blank=True, verbose_name=_("biography (Markdown supported)"))

    #: The location field allows users to specify their location. It is optional and can be left blank.
    location = models.CharField(max_length=255, blank=True, verbose_name=_("location"))

    #: The website field allows users to provide a URL to their personal website or social media profile.
    #: It is optional and can be left blank.
    website = models.URLField(blank=True, verbose_name=_("website"))

    #: The mastodon_url field allows users to provide a URL to their Mastodon profile.
    #: It is optional and can be left blank.
    mastodon_url = models.URLField(blank=True, verbose_name=_("Mastodon profile URL"))

    #: The birth_date field allows users to specify their date of birth. It is optional and can be left blank.
    birth_date = models.DateField(blank=True, null=True, verbose_name=_("birth date"))

    #: The avatar_small field allows users to upload a small profile picture. It is optional and can be left blank.
    #: The uploaded image must be less than 1 MiB in size and is rendered down to 128x128 pixels.
    #: If not provided, the avatar_medium, avatar_large or avatar_full fields can be used as the source for
    #: generating the small avatar size.
    avatar_small = RestrictedImageField(
        upload_to="user/avatars/",
        blank=True,
        null=True,
        max_file_size=1024 * 1024,  # 1 MiB
        verbose_name=_("small profile picture"),
    )

    #: The avatar_medium field allows users to upload a medium profile picture. It is optional and can be left blank.
    #: The uploaded image must be less than 2.5 MiB in size and is rendered down to 256x256 pixels.
    #:
    #: If not provided, the avatar_large or avatar_full fields can be used as the source for
    #: generating the medium avatar size.
    avatar_medium = RestrictedImageField(
        upload_to="user/avatars/",
        blank=True,
        null=True,
        max_file_size=int(2.5 * 1024 * 1024),  # 2.5 MiB
        verbose_name=_("medium profile picture"),
    )

    #: The avatar_large field allows users to upload a large profile picture. It is optional and can be left blank.
    #: The uploaded image must be less than 5 MiB in size and is rendered down to 512x512 pixels.
    #:
    #: If not provided, the avatar_full field can be used as the source for generating the large avatar size.
    avatar_large = RestrictedImageField(
        upload_to="user/avatars/",
        blank=True,
        null=True,
        max_file_size=int(5 * 1024 * 1024),  # 5 MiB
        verbose_name=_("large profile picture"),
    )

    #: The avatar_full field allows users to upload a full-size profile picture. It is optional and can be left blank.
    #: The uploaded image must be less than 10 MiB in size and is not rendered down.
    #:
    #: If avatar_full is uploaded, it can be used as the source for generating the smaller avatar sizes
    #: if the avatar_small, avatar_medium or avatar_large fields are not provided.
    #: This allows users to upload a single high-resolution image that can be used to generate all required
    #: avatar sizes, while still allowing them to upload specific images for each size if they prefer.
    avatar_full = RestrictedImageField(
        upload_to="user/avatars/",
        blank=True,
        null=True,
        max_file_size=int(10 * 1024 * 1024),  # 10 MiB
        verbose_name=_("full size profile picture"),
    )

    @property
    def bio_html(self):
        """
        Return the bio field rendered as HTML using Markdown.

        :return: The bio field rendered as HTML.
        :rtype: SafeString
        """

        from django.utils.safestring import mark_safe

        return mark_safe(markdown.markdown(self.bio, extensions=["extra", "nl2br"]))

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        verbose_name = _("user profile")
        verbose_name_plural = _("user profiles")

        if settings.AUTH_EXTERNAL_MANAGED:
            managed = False
        else:
            managed = True

        db_table = "tinyuser_profile"
        indexes = [
            models.Index(fields=["user"], name="user_idx"),
        ]


class UserProfileSettings(models.Model):
    #: The UserProfile this settings belongs to
    profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, verbose_name=_("user's profile")
    )

    #: The type of settings (e.g. public, members, etc.)
    #:
    #: :value: True
    name = models.CharField(_("Profile name"), max_length=255, default="public")
    key = models.SlugField(_("settings type"), max_length=255, default="public")

    #: Whether the profile is forbidden to view
    #:
    #: :value: True
    is_enabled = models.BooleanField(_("forbid to view my profile"), default=True)

    show_avatar = models.BooleanField(_("show avatar"), default=True)
    #: Whether to show the email address
    #:
    #: :value: False
    show_email = models.BooleanField(_("show email"), default=False)

    #: Whether to show the full name (first_name and last_name)
    #:
    #: :value: False
    show_full_name = models.BooleanField(_("show full name"), default=False)

    #: Configure how to show the birth date.
    #:
    #: Accepted values are
    #: * `date` - Show full date
    #: * `birthday` - Show birthday format with the Year removed
    #: * `no` - Don't show the birth date at all
    #:
    #: :value: no
    show_birth_date = models.CharField(
        max_length=31,
        choices=(
            ("date", _("date")),
            ("birthday", _("birthday")),
            ("no", _("no")),
        ),
        default="no",
    )

    #: Whether to show the website URL
    #:
    #: :value: True
    show_website = models.BooleanField(_("show website"), default=True)

    #: Whether to show the Mastodon URL
    #:
    #: :value: True
    show_mastodon_url = models.BooleanField(_("show mastodon url"), default=True)

    #: Whether to show the biography
    #:
    #: :value: True
    show_bio = models.BooleanField(_("show bigraphy"), default=True)

    #: Whether to show the location of the user
    #:
    #: :value: False
    show_location = models.BooleanField(_("show location"), default=False)

    class Meta:
        db_table = "tinyuser_profile_settings"

        verbose_name = _("profile settings")
        verbose_name_plural = _("profile settings")

        unique_together = [
            ("profile", "key"),
        ]
        indexes = [
            models.Index(fields=["profile"]),
            models.Index(fields=["key"]),
            models.Index(fields=["profile", "key"]),
        ]
