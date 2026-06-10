import os
from logging import getLogger
from pathlib import Path

from django.conf import settings as django_settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.images import ImageFile
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import FormView
from PIL import Image

from django_tinyuser.forms import ProfileForm
from django_tinyuser.mixins.htmx import HtmxMixin
from django_tinyuser.models import TinyUserProfile
from django_tinyuser.settings import TEMP_DIR, TEMPLATE_MAPPING

logger = getLogger(__name__)


class ProfileView(LoginRequiredMixin, HtmxMixin, View):
    """
    View for the user profile page.
    """

    #: Defines the template name for the profile page using the TEMPLATE_MAPPING from settings
    template_name = TEMPLATE_MAPPING["tinyuser/profile"]
    htmx_template_name = TEMPLATE_MAPPING["tinyuser/hx/profile"]

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Handles GET requests for the profile view.

        :param request: The HTTP request object
        :type request: HttpRequest
        :return: The HTTP response with the rendered template
        :rtype: HttpResponse
        """
        instance = TinyUserProfile.objects.get_or_create(user=request.user)[0]
        context = {"profile": instance}
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
    template_name = TEMPLATE_MAPPING["tinyuser/profile/edit"]
    htmx_template_name = TEMPLATE_MAPPING["tinyuser/hx/profile/edit"]

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

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Handles GET requests for the profile view.

        :param request: The HTTP request object
        :type request: HttpRequest
        :return: The HTTP response with the rendered template
        :rtype: HttpResponse
        """
        self.instance = TinyUserProfile.objects.get_or_create(user=request.user)[0]

        return render(
            request,
            self.htmx_template_name if self.is_htmx_request else self.template_name,
            self.get_context_data(),
        )

    def save_avatars(self, instance: TinyUserProfile, files: dict):
        """
        Resizes the avatar image to the specified size.

        :param instance: The TinyUserProfile instance containing the avatar
        :type instance: TinyUserProfile
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

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Handles POST requests for the profile view.

        :param request: The HTTP request object
        :type request: HttpRequest
        :return: The HTTP response with the rendered template
        :rtype: HttpResponse
        """
        self.instance = TinyUserProfile.objects.get_or_create(user=request.user)[0]
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
            except Exception as e:
                logger.error("Error saving profile: %s", e)
                context = self.get_context_data()
                context["failed"] = True
                context["exception"] = str(e)

            return render(
                request,
                self.htmx_template_name if self.is_htmx_request else self.template_name,
                context,
            )
        context = self.get_context_data()
        context["form"] = form
        context["failed"] = True
        return render(
            request,
            self.htmx_template_name if self.is_htmx_request else self.template_name,
            context,
        )
