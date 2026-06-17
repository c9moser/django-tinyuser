from .default import DEFAULT_TEMPLATES


def get_django_templates(css_framework: str) -> dict:
    if css_framework == "bootstrap5":
        from .bootstrap5 import BOOTSTRAP5_TEMPLATES

        ret = dict(DEFAULT_TEMPLATES)
        ret.update(BOOTSTRAP5_TEMPLATES)
        return ret

    elif css_framework == "tailwindcss":
        from .tailwindcss import TAILWINDCSS_TEMPLATES

        ret = dict(DEFAULT_TEMPLATES)
        ret.update(TAILWINDCSS_TEMPLATES)
        return ret
    else:
        return DEFAULT_TEMPLATES
