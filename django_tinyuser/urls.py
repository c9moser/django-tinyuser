from django.urls import path

from django_tinyuser import views
from django_tinyuser import settings

app_name = 'tinyuser'

urlpatterns = [
    path("profile/", views.ProfileView.as_view(), name='profile'),
    path("invite/", views.InviteView.as_view(), name='invite'),
]

if settings.TINYUSER_SHOW_INDEX_PAGE:
    urlpatterns.insert(0, path('', views.IndexView.as_view(), name='index'))
