from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from djoser.views import UserViewSet as DjoserUserViewSet

from .models import (
    Project,
    CustomUser,
)
from .serializers import (
    ProjectsSerialiazer,
    ProjectsCreateSerializer,
)


class UserViewSet(DjoserUserViewSet):


    @action(detail=False, url_name="me/likes/to", url_path="me/likes/to")
    def likes_to(self, request, *args, **kwargs):
        instance = self.request.user
        likes = instance.likes_to.all().select_related("like_to")
        return Response(status=status.HTTP_200_OK)


    @action(detail=False, url_name="me/likes/from", url_path="me/likes/from")
    def likes_from(self, request, *args, **kwargs):
        instance = self.request.user
        likes = instance.likes_from.all().select_related("like_from")
        return Response(status=status.HTTP_200_OK)


class ProjectViewSet(viewsets.GenericViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectsSerialiazer

    def get_serializer_class(self):
        if self.action == ['create', 'update']:
            return ProjectsCreateSerializer
        else:
            return ProjectsSerialiazer

    def list(self, request, *args, **kwargs):
        projects = self.queryset
        serializer = self.serializer_class(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)