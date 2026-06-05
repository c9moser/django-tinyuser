from django_tinyuser import settings


def tinyuser(request):
    return {
        "tinyuser_base_template": settings.BASE_TEMPLATE,
        'SOCIALACCOUNT_ENABLED': settings.SOCIALACCOUNT_ENABLED,
    }
