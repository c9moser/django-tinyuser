from typing import Any

from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import gettext as _


def sidebar(request: HttpRequest) -> list[dict[str, Any]]:
    """
    Returns the sidebar context for the application.
    """
    if request.user.is_authenticated:
        return [
            {
                "title": _("My Account"),
                "bs_icon": "bi-person",
                "children": [
                    {
                        "title": _("Profile"),
                        # "url": reverse("tinyuser:profile"),
                        "bi_icon": "bi-person",
                    },
                    {
                        "title": _("Settings"),
                        # "url": reverse("tinyuser:settings",
                        "bi_icon": "bi-gear",
                    },
                ],
            },
        ]
    else:
        return [
            {
                "title": _("Please log in"),
                "children": [
                    {
                        "title": _("Login"),
                        "url": f"{reverse('account_login')}?next={request.GET.get('next', request.path)}",
                        "bi_icon": "bi-box-arrow-in-right",
                    },
                    {
                        "title": _("Sign Up"),
                        "url": f"{reverse('account_signup')}?next={request.GET.get("next", request.path)}",
                        "bi_icon": "bi-person-plus",
                    },
                ],
            }
        ]


def default_sidebar(request: HttpRequest) -> list[dict[str, Any]]:
    """
    Returns the default sidebar context for the application.
    """
    return sidebar(request)
