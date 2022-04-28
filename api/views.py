from collections import OrderedDict

from django.utils.decorators import method_decorator

from rest_framework import viewsets
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.pagination import PageNumberPagination

from drf_yasg.utils import swagger_auto_schema

from djoser.views import UserViewSet as DjoserUserViewSet

from .permissions import IsOwner
from .models import (
    Project,
    Category,
    CustomUser,
    Callback,
)
from .serializers import (
    ProjectSerializer,
    ProjectCreateSerializer,
    ProjectOfferSerializer,
    ProjectOfferCreateSerializer,
    ProjectDetailSerializer,
    UserSerializer,
    UserDetailSerializer,
    UserCreateSerializer,
    CallbackCreateSerializer,
    UserLikeSerializer,
    ProjectLikeSerializer,
    ProjectNewSerializer,
    ProjectCommentSerializer,
    UserSubscribeSerializer,
)


@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_id="GetUser",
        operation_description="Получение пользователя с указанным `id`",
    ),
)
@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_id="GetUsersList",
        operation_description="Получение списка пользователей",
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_id="CreateUser", operation_description="Создание пользователя"
    ),
)
@method_decorator(name="destroy", decorator=swagger_auto_schema(auto_schema=None))
@method_decorator(name="update", decorator=swagger_auto_schema(auto_schema=None))
@method_decorator(
    name="partial_update", decorator=swagger_auto_schema(auto_schema=None)
)
@method_decorator(name="set_password", decorator=swagger_auto_schema(auto_schema=None))
@method_decorator(name="set_username", decorator=swagger_auto_schema(auto_schema=None))
@method_decorator(name="activation", decorator=swagger_auto_schema(auto_schema=None))
@method_decorator(
    name="resend_activation", decorator=swagger_auto_schema(auto_schema=None)
)
@method_decorator(
    name="reset_username", decorator=swagger_auto_schema(auto_schema=None)
)
@method_decorator(
    name="reset_password", decorator=swagger_auto_schema(auto_schema=None)
)
@method_decorator(
    name="reset_password_confirm", decorator=swagger_auto_schema(auto_schema=None)
)
@method_decorator(
    name="reset_username_confirm", decorator=swagger_auto_schema(auto_schema=None)
)
class UserViewSet(DjoserUserViewSet):
    @swagger_auto_schema(
        method="post",
        operation_id="CreateUserLike",
        operation_description="Создание оценки пользователя",
        request_body=None,
    )
    @action(
        detail=True,
        methods=["post"],
        url_name="likes",
        url_path="likes",
        serializer_class=UserLikeSerializer,
    )
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

    @swagger_auto_schema(operation_id="GetUserForLike")
    @action(
        detail=False,
        methods=["get"],
        url_name="me/likes",
        url_path="me/likes",
        serializer_class=UserSerializer,
        pagination_class=PageNumberPagination,
    )
    def me_likes(self, request, *args, **kwargs):
        """
        Получение списка пользователей для оценки
        """
        liked_users = self.request.user.likes_to.values_list("id", flat=True)
        users = self.queryset.exclude(id__in=liked_users)
        users = users.exclude(id=request.user.id)
        page = self.paginate_queryset(users)
        if page:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_id="GetMyProjects")
    @action(
        detail=False,
        methods=["get"],
        url_name="me/projects",
        url_path="me/projects",
        serializer_class=ProjectSerializer
    )
    def me_projects(self, request, *args, **kwargs):
        """
        Получение списка моих проектов
        """
        projects = request.user.projects.all()
        serializer = self.serializer_class(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_id="GetMyOffers")
    @action(
        detail=False,
        methods=["get"],
        url_name="me/offers",
        url_path="me/offers",
        serializer_class=ProjectOfferSerializer
    )
    def me_offers(self, request, *args, **kwargs):
        """
        Получение списка моих предложений
        """
        offers = request.user.offers.all()
        serializer = self.serializer_class(offers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_id="GetMyLikes")
    @action(
        detail=False,
        url_name="me/likes/to",
        url_path="me/likes/to",
        serializer_class=UserSerializer,
    )
    def likes_to(self, request, *args, **kwargs):
        """
        Получение списка пользователей которых я оценил
        """
        instance = self.request.user
        likes = instance.likes_to.all()
        serializer = self.serializer_class(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_id="GetMeLikes")
    @action(
        detail=False,
        url_name="me/likes/from",
        url_path="me/likes/from",
        serializer_class=UserSerializer,
    )
    def likes_from(self, request, *args, **kwargs):
        """
        Получение списка пользователей оценивших меня
        """
        instance = self.request.user
        likes = instance.likes_from.all()
        serializer = self.serializer_class(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_id="GetMyProjectLikes")
    @action(
        detail=False,
        url_name="me/likes/projects",
        url_path="me/likes/projects",
        serializer_class=ProjectSerializer,
    )
    def like_projects(self, request, *args, **kwargs):
        """
        Получение списка оцененных мной проектов
        """
        instance = self.request.user
        likes = instance.like_projects.all()
        serializer = self.serializer_class(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_id="GetMeProjectLikes")
    @action(
        detail=False,
        url_name="me/projects/likes",
        url_path="me/projects/likes",
        serializer_class=UserSerializer,
    )
    def projects_likes(self, request, *args, **kwargs):
        """
        Получение списка пользователей оценивших мои проекты
        """
        instance = self.request.user
        user_ids = instance.projects.values_list("likes", flat=True)
        likes = CustomUser.objects.filter(id__in=user_ids)
        serializer = self.serializer_class(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_id="CreateSubscribe")
    @action(
        detail=True,
        methods=["post"],
        url_name="subscribe",
        url_path="subscribe",
        serializer_class=UserSubscribeSerializer,
    )
    def subscribe(self, request, id=None):
        """
        Добавление подписки на пользователя с `id`
        """
        data = request.data.copy()
        data["subscriber"] = self.request.user.id
        data["subscription"] = id

        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_id="GetMySubscribers")
    @action(
        detail=False,
        url_name="me/subscribers/",
        url_path="me/subscribers",
        serializer_class=UserSerializer,
    )
    def subscribers(self, request, *args, **kwargs):
        """
        Получение списка моих подписчиков
        """
        instance = self.request.user
        subscribers = instance.subscribers.all()
        serializer = self.serializer_class(subscribers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_id="GetMeSubscriptions")
    @action(
        detail=False,
        url_name="me/subscriptions/",
        url_path="me/subscriptions",
        serializer_class=UserSerializer,
    )
    def subscriptions(self, request, *args, **kwargs):
        """
        Получение списка моих подписок
        """
        instance = self.request.user
        subscriptions = instance.subscriptions.all()
        serializer = self.serializer_class(subscriptions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(method="put", auto_schema=None)
    @swagger_auto_schema(
        method="patch",
        operation_id="UpdateCurrentUser",
        operation_description="Обновление текущего пользователя",
    )
    @swagger_auto_schema(
        method="get",
        operation_id="GetCurrentUser",
        operation_description="Получение текущего пользователя",
    )
    @swagger_auto_schema(
        method="delete",
        operation_id="DeleteCurrentUser",
        operation_description="Удаление текущего пользователя",
    )
    @action(["get", "put", "patch", "delete"], detail=False)
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="GetUserDetail",
        operation_description="Получение детальной информации пользователя с `id`",
    )
    @action(
        detail=True,
        url_name="detail",
        url_path="detail", 
        serializer_class=UserDetailSerializer
    )
    def qdetail(self, request, id=None):
        serializer = self.serializer_class(self.get_object())
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="ValidateUserData",
        operation_description="Предварительная валидация данных пользователя",
    )
    @action(
        detail=False,
        methods=["post"],
        url_name="validate",
        url_path="validate",
        serializer_class=UserCreateSerializer,
        permission_classes=(AllowAny,),
    )
    def validate(self, request):
        fields = request.data.keys()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=False):
            return Response(status=status.HTTP_204_NO_CONTENT)

        errors = [item for item in serializer.errors.items() if item[0] in fields]

        if errors:
            errors = OrderedDict(errors)
            return Response(errors, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectViewSet(viewsets.GenericViewSet):
    queryset = Project
    serializer_class = ProjectSerializer
    permission_classes = (AllowAny,)
    parser_classes = (MultiPartParser,)

    def get_queryset(self):
        queryset = Project.objects.all()
        category = self.request.query_params.get("category")
        if category is not None:
            category = list(category.split(","))
            queryset = queryset.filter(categories__name__in=category)

        country = self.request.query_params.get("country")
        if country is not None:
            queryset = queryset.filter(user__country=country)

        return queryset

    def get_serializer_class(self):
        if self.action in ["create", "update"]:
            return ProjectCreateSerializer
        else:
            return ProjectSerializer

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [IsAuthenticated]
        elif self.action in ["update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsOwner]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    @swagger_auto_schema(operation_id="GetListProjects")
    def list(self, request, *args, **kwargs):
        """
        Получение списка всех проектов
        """
        try:
            projects = self.get_queryset()
        except Project.DoesNotExist:
            return Response(f"Проекты не найдены", status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_id="GetProject")
    def retrieve(self, request, pk):
        """
        Получение проекта с указанным `pk`
        """
        try:
            project = self.queryset.objects.get(id=pk)
        except Project.DoesNotExist:
            return Response(f"Проект {pk} не найден", status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(project)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_id="UpdateProject")
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

    @swagger_auto_schema(
        operation_id="CreateProject", request_body=ProjectCreateSerializer
    )
    def create(self, request, *args, **kwargs):
        """
        Создание проекта
        """
        data = request.data.copy()
        data["user"] = request.user.id

        serializer = self.get_serializer_class()
        serializer = serializer(data=data)
        if serializer.is_valid(raise_exception=False):
            serializer.save(user_id=request.user.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_id="DeleteProject")
    def destroy(self, request, pk):
        """
        Удаление проекта с указанным `pk`
        """
        project = self.get_object()
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(operation_id="GetProjectDetail")
    @action(
        detail=True,
        url_name="detail",
        url_path="detail",
        serializer_class=ProjectDetailSerializer,
    )
    def project_detail(self, request, pk=None):
        """
        Получение детальной информации о проекте с указанным `pk`
        """
        project = self.get_object()
        serializer = self.serializer_class(project)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_id="CreateProjectLike")
    @action(
        detail=True,
        methods=["post"],
        url_name="likes",
        url_path="likes",
        serializer_class=ProjectLikeSerializer,
        parser_classes=(JSONParser,),
    )
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

    @swagger_auto_schema(operation_id="CreateProjectComment")
    @action(
        detail=True,
        methods=["post"],
        url_name="comments",
        url_path="comments",
        serializer_class=ProjectCommentSerializer,
        parser_classes=(JSONParser,),
    )
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

    @action(
        detail=True,
        methods=["post"],
        url_name="news",
        url_path="news",
        serializer_class=ProjectNewSerializer,
        parser_classes=(JSONParser,),
    )
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

    @swagger_auto_schema(operation_id="CreateProjectOffer")
    @action(
        detail=True,
        methods=["post"],
        url_name="offers",
        url_path="offers",
        serializer_class=ProjectOfferCreateSerializer,
        parser_classes=(JSONParser,),
    )
    def offers(self, request, pk=None):
        """
        Добавление предложения от пользователя `request.user` к проекту с указанным `pk`
        """
        data = request.data.copy()
        data["user"] = self.request.user.id
        data["project"] = pk

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


class CategoryAPIView(ListAPIView):
    queryset = Category.objects.all()

    @swagger_auto_schema(operation_id="GetListCategories")
    def get(self, request, *args, **kwargs):
        """
        Получение списка всех категорий
        """
        categories = self.queryset.values_list("name")
        return Response(categories, status=status.HTTP_200_OK)
