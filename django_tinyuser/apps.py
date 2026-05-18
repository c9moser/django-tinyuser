from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class DjangoTinyuserConfig(AppConfig):
    name = 'django_tinyuser'
    verbose_name = _('TinyUser')

    def ready(self):
        from django_tinyuser import settings
        if settings.USE_POSTGRES_SCHEMAS:
            from django.contrib.auth.models import (
                Group,
                GroupPermission,
                Permission,

            )
            from django.contrib.admin.models import (
                LogEntry,
            )
            from django.contrib.contenttypes.models import ContentType
            from allauth.account.models import (
                EmailAddress,
                EmailConfirmation,
            )

            DJANGO_TABLES = [
                Group,
                GroupPermission,
                Permission,
                LogEntry,
                ContentType,
                EmailAddress,
                EmailConfirmation,
            ]

            for model in DJANGO_TABLES:
                model._meta.db_table = f"{settings.DJANGO_POSTGRES_SCHEMA}\".\"{model._meta.db_table}"
