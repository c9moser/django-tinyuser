from django.urls import path, include
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
# You can register your viewsets here, e.g.:
# from .views import UserViewSet
# router.register(r'users', UserViewSet)

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
urlpatterns = [

]
urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('', include(router.urls)),
]
