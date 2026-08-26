# from pathlib import Path

TEMPLATES = {
    "html": {
        "templates": {
            "theme/base": "@tinyuser/base",
            "tinyuser/base": "tinyuser/html/base.dj.html",
            "tinyuser/index": "tinyuser/html/index.html",
            "tinyuser/account/login": "tinyuser/html/account/login.dj.html",
            "tinyuser/account/logout": "tinyuser/html/account/logout.dj.html",
            "tinyuser/account/password_reset": "tinyuser/html/account/password_reset.dj.html",
            "tinyuser/account/profile": "tinyuser/html/account/profile.dj.html",
            "tinyuser/account/settings": "tinyuser/html/account/settings.dj.html",
            "tinyuser/admin/users": "tinyuser/html/admin/users.dj.html",
            "tinyuser/admin/user_detail": "tinyuser/html/admin/user_detail.dj.html",
            "tinyuser/about": "tinyuser/html/about.dj.html",
            "tinyuser/hx/about/authors": "tinyuser/html/hx/about/authors.dj.html",
            "tinyuser/hx/about/translators": "tinyuser/html/hx/about/translators.dj.html",
            "tinyuser/hx/about/dependencies": "tinyuser/html/hx/about/dependencies.dj.html",
            "tinyuser/hx/about/contributors": "tinyuser/html/hx/about/contributors.dj.html",
            "tinyuser/moderate": "tinyuser/html/moderate.dj.html",
            "tinyuser/profile": "tinyuser/html/profile.dj.html",
        },
    },
    "bootstrap5": {
        "templates": {
            "tinyuser/base": "tinyuser/bootstrap5/base.dj.html",
            # "tinyuser/index": "tinyuser/bootstrap5/index.html",
            # "tinyuser/login": "themes/bootstrap5/login.html",
        },
        "settings": {
            "login": {
                "sidebar_enabled": True,
                "navbar_enabled": True,
                "header_enabled": True,
                "footer_enabled": True,
            },
        },
    },
}
