from django.conf import settings
from django_templates.utils import get_logger


def get_tinyuser_logger(name: str):
    prefix = getattr(
        settings,
        "TINYUSER_LOGGER_PREFIX",
        getattr(settings, "LOGGER_PREFIX", "django"),
    )
    return get_logger(name, prefix=prefix)
