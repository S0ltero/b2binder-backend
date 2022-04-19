from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required

from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from api.views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

schema_view = get_schema_view(
   openapi.Info(
      title="B2binder API",
      default_version='v1'
   ),
   public=True,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include('api.urls')),
    path('api/auth/', include(router.urls)),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('redoc/', login_required(schema_view.with_ui('redoc', cache_timeout=0)), name='schema-redoc'),
]
