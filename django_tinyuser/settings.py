"""
Django settings for the TinyUser project.
"""

from django.conf import settings
from django_tinyuser.global_templates.bootstrap import PATH as BOOTSTRAP_TEMPLATES_PATH
from django_tinyuser.global_templates.trailwindcss import PATH as TAILWIND_TEMPLATES_PATH

CSS_FRAMEWORK = getattr(
    settings,
    'TINYUSER_CSS_FRAMEWORK',
    getattr(settings, 'CSS_FRAMEWORK', 'bootstrap')).lower()

CSS_FRAMEWORK_BOOTSTRAP = False
CSS_FRAMEWORK_TAILWIND = False
CSS_FRAMEWORK_CUSTOM = False

if CSS_FRAMEWORK == 'bootstrap':
    CSS_FRAMEWORK_BOOTSTRAP = True
elif CSS_FRAMEWORK == 'tailwindcss':
    CSS_FRAMEWORK_TAILWIND = True
else:
    CSS_FRAMEWORK_CUSTOM = True


USE_POSTGRES_SCHEMAS = getattr(settings, 'USE_POSTGRES_SCHEMAS', False)
DJANGO_POSTGRES_SCHEMA = getattr(
    settings,
    'DJANGO_POSTGRES_SCHEMA',
    getattr(settings, 'POSTGRES_SCHEMA', 'public')
)

TINYUSER_SHOW_INDEX_PAGE = getattr(settings, 'TINYUSER_SHOW_INDEX_PAGE', False)

BASE_TEMPLATE = getattr(
    settings,
    'TINYUSER_BASE_TEMPLATE',
    getattr(settings, 'BASE_TEMPLATE', None)
)

if not BASE_TEMPLATE:
    if CSS_FRAMEWORK_BOOTSTRAP:
        BASE_TEMPLATE = 'django_tinyuser/bootstrap/base.html'
    elif CSS_FRAMEWORK_TAILWIND:
        BASE_TEMPLATE = 'django_tinyuser/tailwindcss/base.html'
    else:
        BASE_TEMPLATE = 'django_tinyuser/html/base.html'
