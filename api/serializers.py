from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.db.models import Sum

from rest_framework import serializers
from rest_framework.authtoken.models import Token
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from .models import (
    CustomUser,
    Project,
    Callback,
    UserLike,
    ProjectLike,
    Category,
    ProjectComment,
    ProjectNew,
    UserSubscribe,
    ProjectOffer,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("name",)


class UserSerializer(serializers.ModelSerializer):
    subscribers = serializers.IntegerField(source="subscribers.count", read_only=True)
    subscriptions = serializers.IntegerField(
        source="subscriptions.count", read_only=True
    )
    count_projects = serializers.IntegerField(source="projects.count", read_only=True)
    count_offers = serializers.IntegerField(source="offers.count", read_only=True)

    class Meta:
        model = CustomUser
        exclude = ('password', 'last_login', 'groups', 'user_permissions',
                    'is_superuser', 'is_active', 'is_staff', 'date_joined')


class UserCreateSerializer(DjoserUserCreateSerializer):
    class Meta:
        model = CustomUser
        exclude = ("last_login", "date_joined",
                   "is_superuser", "is_staff", "is_active",
                   "groups", "user_permissions")

    def validate_password(self, value):
        try:
            validate_password(value, CustomUser)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(serializer_error["non_field_errors"])

        return value


class UserLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLike
        fields = "__all__"


class UserSubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubscribe
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(
        slug_field="name", read_only=True, many=True
    )
    country = serializers.CharField(source="user.country", read_only=True)
    current_investments = serializers.SerializerMethodField()

    class Meta:
        model = Project
        exclude = ("description", "user")

    def get_current_investments(self, obj):
        return obj.offers.aggregate(Sum("amount", default=0))["amount__sum"]


class ProjectCreateSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field="name", many=True
    )

    class Meta:
        model = Project
        fields = "__all__"


class ProjectOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectOffer
        fields = "__all__"



class ProjectOfferCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectOffer
        fields = "__all__"


class ProjectCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectComment
        fields = "__all__"


class ProjectDetailSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(
        slug_field="name", read_only=True, many=True
    )
    comments = ProjectCommentSerializer(read_only=True, many=True)
    offers = ProjectOfferSerializer(read_only=True, many=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = "__all__"


class ProjectLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectLike
        fields = "__all__"


class ProjectNewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectNew
        fields = "__all__"


class UserDetailSerializer(UserSerializer):
    projects = ProjectSerializer(many=True, read_only=True)


class TokenSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="user.id")
    auth_token = serializers.CharField(source="key")

    class Meta:
        model = Token
        fields = ("id", "auth_token")


class CallbackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Callback
        fields = "__all__"
