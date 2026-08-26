from dj_templates.theme import ThemeManager
from django.http import HttpRequest
from django.utils.translation import gettext as _

from dj_tinyuser import settings


def tinyuser(request: HttpRequest):

    theme = ThemeManager.get_global().get_theme(request=request)

    try:
        base_template = theme.get_template("base_template")
    except LookupError:
        base_template = theme.get_template("theme/base")

    tinyuser_templates = {
        "base_template": theme.get_template("theme/base"),
        "login_template": theme.get_template("tinyuser/account/login"),
        "password_reset_template": theme.get_template("tinyuser/account/password_reset"),
        "profile_template": theme.get_template("tinyuser/account/profile"),
        "settings_template": theme.get_template("tinyuser/account/settings"),
    }

    return {
        "socialaccount_enabled": settings.SOCIALACCOUNT_ENABLED,
        "can_sign_up": settings.ALLOW_SIGNUP,
        "invite_allow_all_authenticated_users": settings.INVITE_ALLOW_ALL_AUTHENTICATED_USERS,
        "tinyuser_templates": tinyuser_templates,
    }
