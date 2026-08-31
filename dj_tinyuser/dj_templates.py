# from pathlib import Path

TEMPLATES = {
    "html": {
        "templates": {
            "theme/base": "@tinyuser/base",
            "tinyuser/base": "tinyuser/html/base.dj.html",
            "tinyuser/index": "tinyuser/html/index.html",
            "tinyuser/account/login": "tinyuser/html/account/login.dj.html",
            # "tinyuser/account/logout": "tinyuser/html/account/logout.dj.html",
            "tinyuser/account/password_reset": "tinyuser/html/account/password_reset.dj.html",
            "tinyuser/account/profile": "tinyuser/html/account/profile.dj.html",
            "tinyuser/account/settings": "tinyuser/html/account/settings.dj.html",
            "tinyuser/account/signup": "tinyuser/html/account/signup.dj.html",
            # "tinyuser/admin/users": "tinyuser/html/admin/users.dj.html",
            # "tinyuser/admin/user_detail": "tinyuser/html/admin/user_detail.dj.html",
            # "tinyuser/moderate": "tinyuser/html/moderate.dj.html",
            # "tinyuser/profile": "tinyuser/html/profile.dj.html",
        },
    },
    "bootstrap5": {
        "templates": {
            "tinyuser/base": "tinyuser/bootstrap5/base.dj.html",
            # "tinyuser/index": "tinyuser/bootstrap5/index.html",
            "tinyuser/account/login": "tinyuser/bootstrap5/account/login.dj.html",
            "tinyuser/account/password_reset": "tinyuser/bootstrap5/account/password_reset.dj.html",
            "tinyuser/account/signup": "tinyuser/bootstrap5/account/signup.dj.html",
            "tinyuser/snippets/account.form": "tinyuser/bootstrap5/snippets/account.form.dj.html",
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
    "bs5docs": {
        "templates": {
            # "tinyuser/base": "tinyuser/bs5docs/base.dj.html",
            # "tinyuser/index": "tinyuser/bs5docs/index.html",
            "tinyuser/account/login": "tinyuser/bs5docs/account/login.dj.html",
            "tinyuser/account/signup": "tinyuser/bs5docs/account/signup.dj.html",
            "tinyuser/snippets/account.form": "tinyuser/bs5docs/snippets/account.form.dj.html",
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
