import os
from pathlib import Path
from typing import Any

from django.conf import settings as django_settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.images import ImageFile
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import FormView
from django_templates import get_template
from PIL import Image

from django_tinyuser.forms import ProfileForm, ProfileSettingsForm
from django_tinyuser.logging import get_tinyuser_logger as get_logger
from django_tinyuser.mixins.htmx import HtmxMixin
from django_tinyuser.models import UserProfile, UserProfileSettings
from django_tinyuser.settings import (
    GET_PROFILE,
    PROFILE_DEFAULTS,
    PROFILES,
    TEMP_DIR,
)

logger = get_logger(__name__)


class MyProfileView(LoginRequiredMixin, HtmxMixin, View):
    """
    View for the user profile page.
    """

    #: Defines the template name for the profile page using the TEMPLATE_MAPPING from settings
    template_name = get_template("tinyuser/profile")
    htmx_template_name = get_template("tinyuser/hx/profile")
    profile_settings = {
        "show_avatar": True,
        "show_bio": True,
        "show_birth_date": "date",
        "show_email": True,
        "show_full_name": True,
        "show_location": True,
        "show_mastodon_url": True,
        "show_website": True,
    }

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Handles GET requests for the profile view.

        :param request: The HTTP request object
        :type request: HttpRequest
        :return: The HTTP response with the rendered template
        :rtype: HttpResponse
        """
        profile = UserProfile.objects.get_or_create(user=request.user)[0]
        context = {
            "is_user_profile": True,
            "profile": profile,
            "profile_settings": self.profile_settings,
            "profiles": PROFILES,
        }

        if "profile" in request.GET:
            requested_profile = request.GET["profile"]

            available = False
            for _type, _name in PROFILES:
                if requested_profile == _type:
                    available = True
                    break

            if not available:
                context["profile_warning"] = _(
                    "Profile {profile} is not available."
                ).format(requested_profile)
                try:
                    context["profile_settings"] = UserProfileSettings.objects.get(
                        profile=profile, type="default"
                    )
                except UserProfileSettings.DoesNotExist:
                    profile_settings = dict(self.profile_settings)
                    if PROFILE_DEFAULTS:
                        profile_settings.update(PROFILE_DEFAULTS)
                    context["profile_settings"] = profile_settings
            else:
                try:
                    context["profile_settings"] = UserProfileSettings.objects.get(
                        profile=profile, key=request.GET["profile"]
                    )
                except UserProfileSettings.DoesNotExist:
                    try:
                        context["profile_settings"] = UserProfileSettings.objects.get(
                            profile=profile, key="default"
                        )
                    except UserProfileSettings.DoesNotExist:
                        context["profile_settings"] = PROFILE_DEFAULTS

        return render(
            request,
            self.htmx_template_name if self.is_htmx_request else self.template_name,
            context,
        )


class ProfileView(HtmxMixin, View):
    """
    View for the user profile page.
    """

    #: Defines the template name for the profile page using the TEMPLATE_MAPPING from settings
    template_name = get_template("tinyuser/profile")
    htmx_template_name = get_template("tinyuser/hx/profile")

    def get_profile_settings(self, profile, profile_type):
        profile_settings, created = UserProfileSettings.get_or_create(
            profile=profile, type=profile_type
        )
        if created:
            try:
                default_settings: UserProfileSettings = UserProfileSettings.objects.get(
                    profile=profile, type="default"
                )
                profile_settings.show_avatar = default_settings.show_avatar
                profile_settings.show_bio = default_settings.show_bio
                profile_settings.show_birth_date = default_settings.show_birth_date
                profile_settings.show_email = default_settings.show_email
                profile_settings.show_full_name = default_settings.show_full_name
                profile_settings.show_mastodon_url = default_settings.show_mastodon_url
                profile_settings.show_website = default_settings.show_website
            except UserProfileSettings.DoesNotExist:
                profile_settings.update(**PROFILE_DEFAULTS)
        return profile_settings

    def get(self, request: HttpRequest, user_id: int) -> HttpResponse:
        """
        Handles GET requests for the profile view.

        :param request: The HTTP request object
        :type request: HttpRequest
        :return: The HTTP response with the rendered template
        :rtype: HttpResponse
        """

        user = get_object_or_404(get_user_model(), id=user_id)
        profile = UserProfile.objects.get_or_create(user=request.user)[0]

        if user == request.user:
            profile_settings = MyProfileView.profile_settings
        else:
            if GET_PROFILE:
                get_profile = import_string(GET_PROFILE)
                profile_type = get_profile(request)
            else:
                profile_type = "public"

            profile_settings = self.get_profile_settings(profile, profile_type)

        context = {"profile": profile, "profile_settings": profile_settings}

        return render(
            request,
            self.htmx_template_name if self.is_htmx_request else self.template_name,
            context,
        )


class ProfileEditView(LoginRequiredMixin, HtmxMixin, FormView):
    """
    View for the user profile page.
    """

    #: Defines the template name for the profile page using the TEMPLATE_MAPPING from settings
    template_name = get_template("tinyuser/profile/edit")
    htmx_template_name = get_template("tinyuser/hx/profile/edit")

    #: Defines the form class for the profile view
    form_class = ProfileForm

    def get_context_data(self, **kwargs):
        """
        Retrieves the context data for the profile view.

        :return: Context data for the template
        :rtype: dict
        """
        context = super().get_context_data(**kwargs)
        context["profile"] = self.instance
        if "form" in kwargs:
            context["form"] = kwargs["form"]
        else:
            context["form"] = self.form_class(instance=self.instance)
        return context

    def save_avatars(self, instance: UserProfile, files: dict):
        """
        Resizes the avatar image to the specified size.

        :param instance: The UserProfile instance containing the avatar
        :type instance: UserProfile
        :param size: The target size for the avatar
        :type size: int
        """

        def resize_image(img, size):
            if img.mode in ("RGB", "P"):
                img = img.convert("RGBA")
            width, height = img.size
            if img.width == img.height:
                img = img.resize((size, size))
            if width > height:
                new_height = int(size * height / width)
                img = img.resize((size, new_height))
            else:
                new_width = int(size * width / height)
                img = img.resize((new_width, size))
            return img

        avatar_small_img = None
        avatar_medium_img = None
        avatar_large_img = None

        temp_dir = TEMP_DIR / "avatars"
        temp_dir.mkdir(parents=True, exist_ok=True)

        avatar_small_name = "avatar_{}_small.png".format(instance.user.id)
        avatar_small_path = temp_dir / avatar_small_name
        avatar_small_media = (
            Path(django_settings.MEDIA_ROOT) / "user/avatars" / avatar_small_name
        )
        avatar_small_file = files.get("avatar_small", None)

        avatar_medium_name = "avatar_{}_medium.png".format(instance.user.id)
        avatar_medium_path = temp_dir / avatar_medium_name
        avatar_medium_media = (
            Path(django_settings.MEDIA_ROOT) / "user/avatars" / avatar_medium_name
        )
        avatar_medium_file = files.get("avatar_medium", None)

        avatar_large_name = "avatar_{}_large.png".format(instance.user.id)
        avatar_large_path = temp_dir / avatar_large_name
        avatar_large_media = (
            Path(django_settings.MEDIA_ROOT) / "user/avatars" / avatar_large_name
        )
        avatar_large_file = files.get("avatar_large", None)

        avatar_full_name = "avatar_{}_full.png".format(instance.user.id)
        avatar_full_path = temp_dir / avatar_full_name
        avatar_full_media = (
            Path(django_settings.MEDIA_ROOT) / "user/avatars" / avatar_full_name
        )
        avatar_full_file = files.get("avatar_full", None)

        if avatar_small_file:
            avatar_small_img = Image.open(avatar_small_file.file)
        elif not instance.avatar_small:
            if avatar_medium_file:
                avatar_small_img = Image.open(avatar_medium_file.file)
            elif avatar_large_file:
                avatar_small_img = Image.open(avatar_large_file.file)
            elif avatar_full_file:
                avatar_small_img = Image.open(avatar_full_file.file)

        if avatar_medium_file:
            avatar_medium_img = Image.open(avatar_medium_file.file)
        elif not instance.avatar_medium:
            if avatar_large_file:
                avatar_medium_img = Image.open(avatar_large_file.file)
            elif avatar_full_file:
                avatar_medium_img = Image.open(avatar_full_file.file)

        if avatar_large_file:
            avatar_large_img = Image.open(avatar_large_file.file)
        elif not instance.avatar_large:
            if avatar_full_file:
                avatar_large_img = Image.open(avatar_full_file.file)

        if avatar_small_img:
            avatar_small_img = resize_image(avatar_small_img, 128)
            avatar_small_img.save(avatar_small_path, format="PNG")
            if os.path.exists(avatar_small_media):
                os.remove(avatar_small_media)
            with open(avatar_small_path, "rb") as avatar_small:
                instance.avatar_small.save(
                    avatar_small_path.name, ImageFile(avatar_small)
                )

        if avatar_medium_img:
            avatar_medium_img = resize_image(avatar_medium_img, 256)
            avatar_medium_img.save(avatar_medium_path, format="PNG")
            if os.path.exists(avatar_medium_media):
                os.remove(avatar_medium_media)
            with open(avatar_medium_path, "rb") as avatar_medium:
                instance.avatar_medium.save(
                    avatar_medium_path.name, ImageFile(avatar_medium)
                )

        if avatar_large_img:
            avatar_large_img = resize_image(avatar_large_img, 512)
            avatar_large_img.save(avatar_large_path, format="PNG")
            if os.path.exists(avatar_large_media):
                os.remove(avatar_large_media)
            with open(avatar_large_path, "rb") as avatar_large:
                instance.avatar_large.save(
                    avatar_large_path.name, ImageFile(avatar_large)
                )

        if avatar_full_file:
            avatar_full_img = Image.open(avatar_full_file.file)
            avatar_full_img.save(avatar_full_path, format="PNG", optimize=True)
            if os.path.exists(avatar_full_media):
                os.remove(avatar_full_media)
            with open(avatar_full_path, "rb") as avatar_full:
                instance.avatar_full.save(avatar_full_path.name, ImageFile(avatar_full))

        instance.save()

        for temp_file in [
            avatar_small_path,
            avatar_medium_path,
            avatar_large_path,
            avatar_full_path,
        ]:
            if temp_file.exists():
                temp_file.unlink()

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Handles GET requests for the profile view.

        :param request: The HTTP request object
        :type request: HttpRequest
        :param type: The type of profile edit (e.g., "avatar"), defaults to None
        :type type: str, optional
        :return: The HTTP response with the rendered template
        :rtype: HttpResponse
        """
        self.instance = UserProfile.objects.get_or_create(user=request.user)[0]

        return render(
            request,
            self.htmx_template_name if self.is_htmx_request else self.template_name,
            self.get_context_data(),
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Handles POST requests for the profile view.

        :param request: The HTTP request object
        :type request: HttpRequest
        :return: The HTTP response with the rendered template
        :rtype: HttpResponse
        """
        self.instance = UserProfile.objects.get_or_create(user=request.user)[0]
        form = self.form_class(request.POST, request.FILES, instance=self.instance)
        if form.is_valid():
            try:
                instance = form.save(commit=False)
                self.save_avatars(instance, request.FILES)
                self.instance.refresh_from_db()  # Refresh the instance to get the updated avatars.

                context = self.get_context_data()
                context["success"] = True
                logger.info(
                    "Profile updated successfully for user %s", request.user.email
                )
                request.user.refresh_from_db()
            except Exception as e:
                logger.error("Error saving profile: %s", e)
                context = self.get_context_data()
                context["failed"] = True
                context["exception"] = str(e)
                return render(
                    request,
                    (
                        self.htmx_template_name
                        if self.is_htmx_request
                        else self.template_name
                    ),
                    context,
                )

            if self.is_htmx_request:
                return render(
                    request,
                    self.htmx_template_name,
                    context,
                )
            else:
                return redirect("tinyuser:profile")

        context = self.get_context_data()
        context["form"] = form
        context["failed"] = True
        return render(
            request,
            self.htmx_template_name if self.is_htmx_request else self.template_name,
            context,
        )


class ProfileSettingsView(LoginRequiredMixin, HtmxMixin, View):
    """
    View for managing user profile settings.
    """

    def get_context_data(
        self, form: ProfileSettingsForm | None = None, **kwargs
    ) -> dict[str, Any]:
        if form is None:
            form = ProfileSettingsForm(instance=self.instance)

        context = kwargs
        context["form"] = form

        return context

    def init_variables(self, profile_key: str):
        if not profile_key:
            if len(PROFILES) == 1:
                self.profile_type, self.profile_name = PROFILES[0]
            else:
                self.profile_type, self.profile_name = "default", _("default")
        else:
            profile_exists = False
            for _profile_key, _profile_name in PROFILES:
                if _profile_key == profile_key:
                    self.profile_type = profile_key
                    self.profile_name = _profile_name
                    profile_exists = True

            if not profile_exists:
                raise Http404(
                    _('No such profile "{profile}"').format(profile=profile_key)
                )

            self.db_profile = UserProfile.objects.get_or_create(user=self.request.user)[
                0
            ]
            self.instance = UserProfileSettings.objects.get_or_create(
                profile=self.db_profile, type=profile_key
            )[0]

    def get(self, request: HttpRequest, profile: str) -> HttpResponse:
        self.init_variables(profile)

        return render(
            request,
            self.htmx_template_name if self.is_htmx_request else self.template_name,
            self.get_context_data(),
        )

    def post(self, request: HttpRequest, profile: str) -> HttpResponse:
        self.init_variables(profile)
        form = ProfileSettingsForm(request.POST, instance=self.instance)
        if form.is_valid():
            form.save()
            context = self.get_context_data(form=form, success=True)
        else:
            context = self.get_context_data(form=form, failed=True)

        return render(
            request,
            (self.htmx_template_name if self.is_htmx_request else self.template_name),
            context,
        )


# class ProfileSettingsView(LoginRequiredMixin, View):
#    def create_form(self, profile_type: str) -> ProfileSettingsForm:
#        # return UserProfileSettings.create_settings(profile_type)
#        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
#        if created:
#            logger.info(f"Created profile for user {self.request.user.username}")
#
#        form = ProfileSettingsForm(instance=profile)
#        return form
#
#    def get(self, request: HttpRequest, profile: str | None = None) -> HttpResponse:
#        if not getattr(request.user, "tinyuser_profile", None):
#            return HttpResponseRedirect(reverse("profile:settings"))
#
#        tu_profile = getattr(request.user, "tinyuser_profile", None)
#        if not tu_profile:
#            return HttpResponseRedirect(reverse("tinyuser:profile"))
#
#        if not profile:
#            profile_settings = UserProfileSettings.objects.filter(profile=tu_profile)[0]
##
#            if not profile_settings:
#                profile_settings = UserProfileSettings.objects.create(
#                    profile=UserProfile.objects.get(user=request.user),
#                    name=_("Default"),
#                    key="default",
#                )
#        else:
#            profile_settings = UserProfileSettings.objects.filter(
#                profile=request.user.tinyuser_profile, key=profile
#            )[0]
#            self.instance = profile_settings
#
#        return render(
#            request, self.template_name, context={"profile": profile_settings}
#        )
