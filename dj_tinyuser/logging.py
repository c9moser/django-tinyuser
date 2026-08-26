from dj_templates.utils.logging import get_logger
from django.conf import settings


def get_tinyuser_logger(name: str):
    prefix = getattr(
        settings,
        "TINYUSER_LOGGER_PREFIX",
        getattr(settings, "LOGGER_PREFIX", "django"),
    )
    return get_logger(name, prefix=prefix)
