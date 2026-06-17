from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoTinyuserConfig(AppConfig):
    name = "django_tinyuser"
    verbose_name = _("TinyUser")
