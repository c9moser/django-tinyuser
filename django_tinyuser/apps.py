from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoTinyuserConfig(AppConfig):
    name = 'django_tinyuser'
    verbose_name = _('TinyUser')

    def ready(self):
        from django_tinyuser import settings

        if settings.USE_POSTGRESQL_SCHEMAS:
            # Inject the PostgreSQL schema into the db_table of all models of the auth
            # and contenttypes apps, as well as allauth if installed.
            from django.db.models import Model

            models = []
            from django.contrib.auth import models as auth_models
            for item in dir(auth_models):
                attr = getattr(auth_models, item)
                if isinstance(attr, type) and issubclass(attr, Model):
                    models.append(attr)

            from django.contrib.contenttypes import models as contenttypes_models
            for item in dir(contenttypes_models):
                attr = getattr(contenttypes_models, item)
                if isinstance(attr, type) and issubclass(attr, Model):
                    models.append(attr)

            from allauth.account import models as allauth_models
            for item in dir(allauth_models):
                attr = getattr(allauth_models, item)
                if isinstance(attr, type) and issubclass(attr, Model):
                    models.append(attr)

            from allauth.socialaccount import models as allauth_social_models
            for item in dir(allauth_social_models):
                attr = getattr(allauth_social_models, item)
                if isinstance(attr, type) and issubclass(attr, Model):
                    models.append(attr)

            for model in models:
                model._meta.db_table = f"{settings.DJANGO_POSTGRES_SCHEMA}\".\"{model._meta.db_table}"
                if settings.AUTH_EXTERNAL_MANAGED:
                    model._meta.managed = False
                else:
                    model._meta.managed = True
