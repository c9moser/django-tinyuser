"""
Django settings for the TinyUser project.
"""

from pathlib import Path

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from django_tinyuser.global_templates.bootstrap5 import (
    PATH as BOOTSTRAP_TEMPLATES_PATH,  # noqa: F401
)
from django_tinyuser.global_templates.trailwindcss import (
    PATH as TAILWIND_TEMPLATES_PATH,  # noqa: F401
)

ALLOW_SIGNUP = getattr(settings, "ALLOW_SIGNUP", True)

INVITE_ALLOW_ALL_AUTHENTICATED_USERS = getattr(
    settings, "INVITE_ALLOW_ALL_AUTHENTICATED_USERS", False
)
INVITE_GROUPS = getattr(settings, "INVITE_GROUPS", [])

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


PROFILES = getattr(
    settings,
    "TINYUSER_PROFILES",
    [
        ("public", _("public")),
    ],
)

PROFILE_DEFAULTS: dict = getattr(
    settings,
    "TINYUSER_PROFILE_DEFAULTS",
    {
        "enabled": True,
        "show_email": False,
        "show_full_name": False,
        "show_location": True,
        "show_bio": True,
        "show_website": True,
        "show_mastodon_url": True,
        "show_birth_date": "birthday",
    },
)

GET_PROFILE = getattr(settings, "TINYUSER_GET_PROFILE", None)
BRAND = getattr(settings, "BRAND", _("TinyUser"))

if not PROFILES:
    PROFILES = ("public", _("public"))
if len(PROFILES) > 1:
    # ensure that we have a 'default' group if the len(PROFILE_TYPES) > 1
    _found = False
    for _id, _name in PROFILES:
        if _id == "default":
            _found = True
            break

    if not _found:
        PROFILES.insert(0, ("default", _("default")))

    del _found
