from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter
from api.views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')


urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include('api.urls')),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include(router.urls)),
    path('api/auth/', include('djoser.urls.authtoken')),
]
