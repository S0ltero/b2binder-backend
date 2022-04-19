from rest_framework import viewsets
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from djoser.views import UserViewSet as DjoserUserViewSet

from .permissions import IsOwner
from .models import (
    Project,
    CustomUser,
    Callback,
)
from .serializers import (
    ProjectsSerializer,
    ProjectsCreateSerializer,
    ProjectsDetailSerializer,
    UserSerializer,
    UserCreateSerializer,
    CallbackCreateSerializer,
    UserLikeSerializer,
    ProjectLikeSerializer,
    ProjectNewSerializer,
    ProjectCommentSerializer,
    UserSubscribeSerializer,
    ProjectOfferSerializer
)


class UserViewSet(DjoserUserViewSet):

    queryset = CustomUser
    permission_classes = (IsAuthenticated, )

    @action(detail=True, methods=['post'], url_name='likes', url_path='likes',
            serializer_class=UserLikeSerializer)
    def likes(self, request, id=None):
        data = request.data.copy()
        data["like_from"] = self.request.user.id
        data["like_to"] = id

        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, url_name="me/likes/to", url_path="me/likes/to",
            serializer_class=UserSerializer)
    def likes_to(self, request, *args, **kwargs):
        """
        Получение списка пользователей которых я оценил
        """
        instance = self.request.user
        likes = instance.likes_to.all()
        serializer = self.serializer_class(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, url_name="me/likes/from", url_path="me/likes/from",
            serializer_class=UserSerializer)
    def likes_from(self, request, *args, **kwargs):
        """
        Получение списка пользователей оценивших меня
        """
        instance = self.request.user
        likes = instance.likes_from.all()
        serializer = self.serializer_class(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, url_name="me/likes/projects", url_path="me/likes/projects",
            serializer_class=ProjectsSerializer)
    def like_projects(self, request, *args, **kwargs):
        """
        Получение списка оцененных мной проектов
        """
        instance = self.request.user
        likes = instance.like_projects.all()
        serializer = self.serializer_class(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, url_name="me/projects/likes", url_path="me/projects/likes",
            serializer_class=UserSerializer)
    def projects_likes(self, request, *args, **kwargs):
        """
        Получение списка пользователей оценивших мои проекты
        """
        instance = self.request.user
        user_ids = instance.projects.values_list("likes", flat=True)
        likes = CustomUser.objects.filter(id__in=user_ids)
        serializer = self.serializer_class(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_name='subscribe', url_path='subscribe',
            serializer_class=UserSubscribeSerializer)
    def subscribe(self, request, id=None):
        """
        Добавление подписки на пользователя с `id`
        """
        data = request.data.copy()
        data['subscriber'] = self.request.user.id
        data['subscription'] = id

        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, url_name='me/subscribers/', url_path='me/subscribers',
            serializer_class=UserSerializer)
    def subscribers(self, request, *args, **kwargs):
        """
        Получение списка моих подписчиков
        """
        instance = self.request.user
        subscribers = instance.subscribers.all()
        serializer = self.serializer_class(subscribers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProjectViewSet(viewsets.GenericViewSet):
    queryset = Project
    serializer_class = ProjectsSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        queryset = Project.objects.all()
        category = self.request.query_params.get('category')
        if category is not None:
            category = list(category.split(','))
            queryset = queryset.filter(categories__name__in=category)

        country = self.request.query_params.get('country')
        if country is not None:
            queryset = queryset.filter(user__country=country)

        return queryset

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return ProjectsCreateSerializer
        else:
            return ProjectsSerializer

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [IsAuthenticated]
        elif self.action in ["update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsOwner]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        """
        Получение списка всех проектов
        """
        try:
            projects = self.get_queryset()
        except Project.DoesNotExist:
            return Response(f'Проекты не найдены', status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk):
        """
        Получение проекта с указанным `pk`
        """
        try:
            project = self.queryset.objects.get(id=pk)
        except Project.DoesNotExist:
            return Response(f'Проект {pk} не найден', status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(project)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk):
        """
        Обновление проекта с указанным `pk`
        """
        project = self.get_object()
        serializer = self.serializer_class(project, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=False):
            serializer.update(project, serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        """
        Создание проекта
        """
        data = request.data.copy()
        data['user'] = request.user.id

        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=False):
            serializer.save(user_id=request.user.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        """
        Удаление проекта с указанным `pk`
        """
        project = self.get_object()
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, url_name='detail', url_path='detail',
            serializer_class=ProjectsDetailSerializer)
    def project_detail(self, request, pk=None):
        """
        Получение детальной информации о проекте с указанным `pk`
        """
        project = self.get_object()
        serializer = self.serializer_class(project)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_name='likes', url_path='likes',
            serializer_class=ProjectLikeSerializer)
    def project_likes(self, request, pk=None):
        """
        Добавление оценки от пользователя `request.user` к проекту с указанным `pk`
        """
        data = request.data.copy()
        data["project"] = pk
        data["user"] = self.request.user.id

        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_name='comments', url_path='comments',
            serializer_class=ProjectCommentSerializer)
    def comments(self, request, pk=None):
        """
        Добавление комментария от пользователя `request.user` к проекту с указанным `pk`
        """
        data = request.data.copy()
        data["project"] = pk
        data["user"] = self.request.user.id

        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_name='news', url_path='news',
            serializer_class=ProjectNewSerializer)
    def news(self, request, pk=None):
        data = request.data.copy()
        data["project"] = pk
        data["user"] = self.request.user.id

        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_name='offers', url_path='offers',
            serializer_class=ProjectOfferSerializer)
    def offers(self, request, pk=None):
        """
        Добавление предложения от пользователя `request.user` к проекту с указанным `pk`
        """
        data = request.data.copy()
        data['user'] = self.request.user.id
        data['project'] = pk

        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CallbackAPIView(CreateAPIView):
    """
    Добавление обратной связи
    """
    queryset = Callback.objects.all()
    serializer_class = CallbackCreateSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
