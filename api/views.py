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
    queryset = Project
    serializer_class = ProjectsSerialiazer

    def get_serializer_class(self):
        if self.action == ['create', 'update']:
            return ProjectsCreateSerializer
        else:
            return ProjectsSerialiazer

    def list(self, request, *args, **kwargs):
        projects = self.queryset.objects.all()
        serializer = self.serializer_class(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk):
        try:
            project = self.queryset.objects.get(id=pk)
        except Project.DoesNotExist:
            return Response(f'Проект {pk} не найден', status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(project)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        pk = request.data['id']
        try:
            project = self.queryset.objects.get(id=pk)
        except Project.DoesNotExist:
            return Response(f'Проект {pk} не найден', status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(project, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=False):
            serializer.update(project, serializer.validated_data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = request.user.id

        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=False):
            serializer.save(user_id=request.user.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)