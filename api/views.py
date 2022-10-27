from collections import OrderedDict

from django.utils import timezone

from rest_framework import viewsets
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.pagination import PageNumberPagination

from djoser.views import UserViewSet as DjoserUserViewSet
from yookassa.domain.notification import WebhookNotification, WebhookNotificationEventType
from yookassa.domain.common import SecurityHelper

from .permissions import IsOwner, HasSubscription
from .models import (
    Project,
    Category,
    CustomUser,
    Callback,
    Payment,
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
from .payment import create_payment


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10


class PaymentView(APIView):

    def post(self, request):
        # Check if ip address in trusted origins
        ip = request.META.get("REMOTE_ADDR")
        if not SecurityHelper().is_ip_trusted(ip):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Check if request.data object is valid
        try:
            notification = WebhookNotification(request.body)
        except Exception:
            pass

        # Check if user from payment metadata exists
        try:
            user = CustomUser.objects.get(pk=notification.object.metadata.get("userId"))
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Get or create payment object by payment id
        payment, _ = Payment.objects.get_or_create(
            payment_id=notification.object.id,
            defaults={
                "user": user
            }
        )

        if notification.object.amount == 500:
            timedelta = timezone.timedelta(days=30)
        elif notification.object.amount == 700:
            timedelta = timezone.timedelta(days=60)

        if notification.event == WebhookNotificationEventType.PAYMENT_SUCCEEDED:
            # Update user subscription status
            user.subscription_end_at += timedelta
            user.has_subscribe = True
            user.save()

            # Update Payment object
            payment.status = Payment.Status.SUCCEEDED
            payment.save()
        elif notification.event == WebhookNotificationEventType.PAYOUT_CANCELED:
            # Update Payment object
            payment.status = Payment.Status.SUCCEEDED
            payment.save()
        elif notification.event == WebhookNotificationEventType.REFUND_SUCCEEDED:
            # Update user subscription status
            user.subscription_end_at -= timedelta
            if user.subscription_end_at < timezone.now():
                user.has_subscribe = False
            user.save()

            # Update Payment object
            payment.status = Payment.Status.REFUNDED
            payment.save()

        return Response(status=status.HTTP_200_OK)


class UserViewSet(DjoserUserViewSet):
    pagination_class = StandardResultsSetPagination

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

    @action(
        detail=False,
        methods=["get"],
        url_name="me/likes",
        url_path="me/likes",
        serializer_class=UserSerializer,
        permission_classes=(HasSubscription,)
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

    @action(
        detail=False,
        methods=["get"],
        url_name="me/projects",
        url_path="me/projects",
        serializer_class=ProjectSerializer
    )
    def projects(self, request, *args, **kwargs):
        """
        Получение списка моих проектов
        """
        projects = request.user.projects.all()
        serializer = self.serializer_class(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get"],
        url_name="me/offers",
        url_path="me/offers",
        serializer_class=ProjectOfferSerializer,
        permission_classes=(HasSubscription,)
    )
    def offers(self, request, *args, **kwargs):
        """
        Получение списка моих предложений
        """
        offers = request.user.offers.all()
        serializer = self.serializer_class(offers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

    @action(
        detail=True,
        url_name="detail",
        url_path="detail", 
        serializer_class=UserDetailSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def qdetail(self, request, id=None):
        serializer = self.serializer_class(self.get_object())
        return Response(serializer.data, status=status.HTTP_200_OK)

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
    pagination_class = StandardResultsSetPagination
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
        elif self.action in ["list", "retrieve", "detail", "likes", "comments", "news", "offers"]:
            self.permission_classes = [HasSubscription]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        """
        Получение списка всех проектов
        """
        projects = self.get_queryset()

        page = self.paginate_queryset(projects)
        if page:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk):
        """
        Получение проекта с указанным `pk`
        """
        project = self.get_object()
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
        data["user"] = request.user.id

        serializer = self.get_serializer_class()
        serializer = serializer(data=data)
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

    def get(self, request, *args, **kwargs):
        """
        Получение списка всех категорий
        """
        categories = self.queryset.values_list("name")
        return Response(categories, status=status.HTTP_200_OK)
