from django.urls import path

from django_tinyuser import views
from django_tinyuser import settings

app_name = 'tinyuser'

urlpatterns = [
    ]

if settings.TINYUSER_SHOW_INDEX_PAGE:
    urlpatterns.insert(0, path('', views.IndexView.as_view(), name='index'))
