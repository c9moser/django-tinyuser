from django.urls import path

from django_tinyuser import views
from django_tinyuser import settings

app_name = 'tinyuser'

urlpatterns = [
    path("tinyuser/", views.IndexView.as_view(), name='tinyuser'),
    path("accounts/profile/", views.ProfileView.as_view(), name='profile'),
    path("accounts/invite/", views.InviteView.as_view(), name='invite'),
]

if settings.TINYUSER_SHOW_INDEX_PAGE:
    urlpatterns += [
        path("", views.IndexView.as_view(), name='index'),
    ]
