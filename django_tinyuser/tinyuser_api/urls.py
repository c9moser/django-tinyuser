from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'tinyuser.api'

router = DefaultRouter()
# You can register your viewsets here, e.g.:
# from .views import UserViewSet
# router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('accounts/create/', views.CreateUserView.as_view(), name='user-create'),

]
