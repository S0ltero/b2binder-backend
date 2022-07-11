from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from rest_framework.routers import DefaultRouter

from api.views import UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthcheck/", lambda r: HttpResponse()),
    path("api/", include("api.urls")),
    path("api/auth/", include(router.urls)),
    path("api/auth/", include("djoser.urls.authtoken")),
    path(
        "docs/",
        login_required(
            TemplateView.as_view(
                template_name="docs.html",
            )
        )
    )
]
