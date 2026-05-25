"""
URL configuration for django_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django_tinyuser.tinyuser_api import urls as tinyuser_api_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('django_tinyuser.urls')),
    path("invitations/", include('invitations.urls', namespace='invitations'))
]

if 'rest_framework' in settings.INSTALLED_APPS:
    urlpatterns += [
        path('api/accounts/', include('rest_framework.urls', namespace='rest_framework')),
    ]

if 'drf_spectacular' in settings.INSTALLED_APPS:
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularSwaggerView,
        SpectacularRedocView
    )
    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
        path(
            'api/doc/',
            SpectacularSwaggerView.as_view(url_name='api-schema'),
            name='api-doc'
        ),
        path(
            'api/redoc/',
            SpectacularRedocView.as_view(url_name='api-schema'),
            name='api-redoc'
        ),
    ]




urlpatterns += [
    path('api/', include(tinyuser_api_urls)),
]

if settings.DEBUG:
    urlpatterns += [
        path("", include("django_tinyuser.urls")),
        path('__debug__/', include('debug_toolbar.urls')),
        path('__reload__/', include('django_browser_reload.urls')),
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
        *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
    ]
