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


USE_POSTGRESQL_SCHEMAS = getattr(settings, 'USE_POSTGRESQL_SCHEMAS', False)
POSTGRESQL_AUTH_SCHEMA = getattr(settings, 'POSTGRESQL_AUTH_SCHEMA', 'public')
TINYUSER_EXTERNAL_MANAGED = getattr(settings, 'TINYUSER_EXTERNAL_MANAGED', False)
AUTH_EXTERNAL_MANAGED = getattr(settings, 'AUTH_EXTERNAL_MANAGED', False)

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

ALLOW_SIGNUP = getattr(settings, 'ALLOW_SIGNUP', True)
DEFAULT_USER_GROUPS = getattr(settings, 'DEFAULT_USER_GROUPS', [])
