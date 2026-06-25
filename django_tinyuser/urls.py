from django.urls import path

from django_tinyuser import settings, views

app_name = "tinyuser"

urlpatterns = [
    path("user/", views.IndexView.as_view(), name="user"),
    path("user/profile", views.MyProfileView.as_view(), name="profile"),
    path("accounts/profile/", views.ProfileEditView.as_view(), name="profile-edit"),
    path(
        "accounts/profile/settings/",
        views.ProfileSettingsView.as_view(),
        name="profile-settings",
    ),
    path("accounts/invite/", views.InviteView.as_view(), name="invite"),
]

if settings.TINYUSER_SHOW_INDEX_PAGE:
    urlpatterns += [
        path("", views.IndexView.as_view(), name="index"),
    ]
