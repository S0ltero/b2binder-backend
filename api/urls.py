from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import *


router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='projects')

urlpatterns = [
    path('callback/', CallbackAPIView.as_view(), name='callback'),
    path('categories/', CategoryAPIView.as_view(), name='categories')
] + router.urls