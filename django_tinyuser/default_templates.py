BOOTSTRAP_TEMPLATES = {
    "tinyuser/base": "django_tinyuser/bootstrap/base.html",
    "tinyuser/hx/invite": "django_tinyuser/bootstrap/invite/hx/invite.html",
    "tinyuser/hx/invite/failed": "django_tinyuser/bootstrap/invite/hx/failed.html",
    "tinyuser/hx/invite/success": "django_tinyuser/bootstrap/invite/hx/success.html",
    "tinyuser/hx/profile": "django_tinyuser/bootstrap/profile/hx/profile.html",
    "tinyuser/hx/profile/edit": "django_tinyuser/bootstrap/profile/hx/edit.html",
    "tinyuser/index": "django_tinyuser/bootstrap/index/index.html",
    "tinyuser/invite": "django_tinyuser/bootstrap/invite/invite.html",
    "tinyuser/invite/success": "django_tinyuser/bootstrap/invite/success.html",
    "tinyuser/invite/failed": "django_tinyuser/bootstrap/invite/failed.html",
    "tinyuser/profile": "django_tinyuser/bootstrap/profile/profile.html",
    "tinyuser/profile/edit": "django_tinyuser/bootstrap/profile/edit.html",
}

TAILWIND_TEMPLATES = {
    "tinyuser/base": "django_tinyuser/tailwindcss/base.html",
    "tinyuser/hx/invite": "django_tinyuser/tailwindcss/invite/hx/invite.html",
    "tinyuser/hx/invite/failed": "django_tinyuser/tailwindcss/invite/hx/failed.html",
    "tinyuser/hx/invite/success": "django_tinyuser/tailwindcss/invite/hx/success.html",
    "tinyuser/hx/profile": "django_tinyuser/tailwindcss/profile/hx/profile.html",
    "tinyuser/index": "django_tinyuser/tailwindcss/index/index.html",
    "tinyuser/invite": "django_tinyuser/tailwindcss/invite/invite.html",
    "tinyuser/invite/success": "django_tinyuser/tailwindcss/invite/success.html",
    "tinyuser/invite/failed": "django_tinyuser/tailwindcss/invite/failed.html",
    "tinyuser/profile": "django_tinyuser/tailwindcss/profile/profile.html",
    "tinyuser/profile/edit": "django_tinyuser/tailwindcss/profile/edit.html",
}


CUSTOM_TEMPLATES = {
    "tinyuser/base": "django_tinyuser/html/base.html",
    "tinyuser/hx/invite": "django_tinyuser/html/invite/hx/invite.html",
    "tinyuser/hx/invite/failed": "django_tinyuser/html/invite/hx/failed.html",
    "tinyuser/hx/invite/success": "django_tinyuser/html/invite/hx/success.html",
    "tinyuser/hx/profile": "django_tinyuser/html/profile/hx/profile.html",
    "tinyuser/index": "django_tinyuser/html/index/index.html",
    "tinyuser/invite": "django_tinyuser/html/invite/invite.html",
    "tinyuser/invite/success": "django_tinyuser/html/invite/success.html",
    "tinyuser/invite/failed": "django_tinyuser/html/invite/failed.html",
    "tinyuser/profile": "django_tinyuser/html/profile/profile.html",
    "tinyuser/profile/edit": "django_tinyuser/html/profile/edit.html",
}


def clean():
    """
    Cleans up the default templates by deleting the template dictionaries.
    """
    global BOOTSTRAP_TEMPLATES
    del BOOTSTRAP_TEMPLATES

    global TAILWIND_TEMPLATES
    del TAILWIND_TEMPLATES

    global CUSTOM_TEMPLATES
    del CUSTOM_TEMPLATES
