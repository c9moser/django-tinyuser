"""
Django settings for the TinyUser project.
"""

from pathlib import Path

from django.conf import settings

from django_tinyuser.default_templates import CUSTOM_TEMPLATES
from django_tinyuser.default_templates import clean as clean_default_templates
from django_tinyuser.global_templates.bootstrap import PATH as BOOTSTRAP_TEMPLATES_PATH
from django_tinyuser.global_templates.trailwindcss import (
    PATH as TAILWIND_TEMPLATES_PATH,
)

ALLOW_SIGNUP = getattr(settings, "ALLOW_SIGNUP", True)

INVITE_ALLOW_ALL_AUTHENTICATED_USERS = getattr(
    settings, "INVITE_ALLOW_ALL_AUTHENTICATED_USERS", False
)
INVITE_GROUPS = getattr(settings, "INVITE_GROUPS", [])


LOGGER_PREFIX = getattr(
    settings,
    "TINYTOOLS_LOGGER_PREFIX",
    getattr(
        settings, "TINYUSER_LOGGER_PREFIX", getattr(settings, "LOGGER_PREFIX", "django")
    ),
)

CSS_FRAMEWORK = getattr(
    settings, "TINYUSER_CSS_FRAMEWORK", getattr(settings, "CSS_FRAMEWORK", "bootstrap")
).lower()

CSS_FRAMEWORK_BOOTSTRAP = False
CSS_FRAMEWORK_TAILWIND = False
CSS_FRAMEWORK_CUSTOM = False

if CSS_FRAMEWORK == "bootstrap":
    CSS_FRAMEWORK_BOOTSTRAP = True
elif CSS_FRAMEWORK == "tailwindcss":
    CSS_FRAMEWORK_TAILWIND = True
else:
    CSS_FRAMEWORK_CUSTOM = True

SOCIALACCOUNT_ENABLED = getattr(settings, "SOCIALACCOUNT_ENABLED", False)
USE_POSTGRESQL_SCHEMAS = getattr(settings, "USE_POSTGRESQL_SCHEMAS", False)
POSTGRESQL_AUTH_SCHEMA = getattr(settings, "POSTGRESQL_AUTH_SCHEMA", "public")
TINYUSER_EXTERNAL_MANAGED = getattr(settings, "TINYUSER_EXTERNAL_MANAGED", False)
AUTH_EXTERNAL_MANAGED = getattr(settings, "AUTH_EXTERNAL_MANAGED", False)

TINYUSER_SHOW_INDEX_PAGE = getattr(settings, "TINYUSER_SHOW_INDEX_PAGE", False)
INVITE_GROUP_NAME = getattr(settings, "TINYUSER_INVITE_GROUP_NAME", None)
INVITE_ALLOW_ALL_AUTHENTICATED_USERS = getattr(
    settings, "TINYUSER_INVITE_ALLOW_ALL_AUTHENTICATED_USERS", False
)

DEFAULT_USER_GROUPS = getattr(settings, "DEFAULT_USER_GROUPS", [])

BASE_TEMPLATE = getattr(
    settings, "TINYUSER_BASE_TEMPLATE", getattr(settings, "BASE_TEMPLATE", None)
)

if not BASE_TEMPLATE:
    if CSS_FRAMEWORK_BOOTSTRAP:
        BASE_TEMPLATE = "django_tinyuser/bootstrap/base.html"
    elif CSS_FRAMEWORK_TAILWIND:
        BASE_TEMPLATE = "django_tinyuser/tailwindcss/base.html"
    else:
        BASE_TEMPLATE = "django_tinyuser/html/base.html"

TEMPLATE_MAPPING = getattr(
    settings, "TINYUSER_TEMPLATES", getattr(settings, "TEMPLATES_MAPPING", {})
)

TEMP_DIR = Path(
    getattr(settings, "TEMP_DIR", settings.BASE_DIR / ".data" / "temp")
).resolve()

if CSS_FRAMEWORK_BOOTSTRAP:
    from django_tinyuser.default_templates import BOOTSTRAP_TEMPLATES

    for key, value in BOOTSTRAP_TEMPLATES.items():
        TEMPLATE_MAPPING.setdefault(key, value)
elif CSS_FRAMEWORK_TAILWIND:
    from django_tinyuser.default_templates import TAILWIND_TEMPLATES

    for key, value in TAILWIND_TEMPLATES.items():
        TEMPLATE_MAPPING.setdefault(key, value)
else:
    for key, value in CUSTOM_TEMPLATES.items():
        TEMPLATE_MAPPING.setdefault(key, value)

clean_default_templates()
