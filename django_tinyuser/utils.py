
from django.conf import settings


def get_base_template():
    """Returns the base template path based on the CSS framework setting."""
    return settings.BASE_TEMPLATE


def get_tinyuser_template(template_name):
    """Returns the template path for a given template name based on the CSS framework setting."""

    css_framework = settings.CSS_FRAMEWORK
    if css_framework == 'bootstrap':
        return f'django_tinyuser/bootstrap/{template_name}'
    elif css_framework == 'tailwindcss':
        return f'django_tinyuser/tailwindcss/{template_name}'
    else:
        return f'django_tinyuser/html/{template_name}'
