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
    ProjectOffer
)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', )


class UserSerializer(serializers.ModelSerializer):
    subscribers = serializers.IntegerField(source="subscribers.count", read_only=True)
    subscriptions = serializers.IntegerField(source="subscriptions.count", read_only=True)

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
        fields = ('like_to', 'like_from')


class UserSubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserSubscribe
        fields = ('subscriber', 'subscription')


class ProjectsSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)
    current_investments =  serializers.SerializerMethodField()

    class Meta:
        model = Project
                  'profit', 'investments', 'current_investments')

    def get_current_investments(self, obj):
        return obj.offers.aggregate(Sum('amount'))['amount__sum']


class ProjectsCreateSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)

    class Meta:
        model = Project
        exclude = ('user',)


class ProjectOfferSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectOffer
        fields = ('user', 'project', 'amount')


class ProjectsDetailSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)
    offers = ProjectOfferSerializer(read_only=True, many=True)

    class Meta:
        model = Project
        fields = '__all__'


class ProjectLikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectLike
        fields = ('user', 'project')


class ProjectCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectComment
        fields = ('user', 'project', 'text')


class ProjectNewSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectNew
        fields = ('user', 'project', 'text')


class TokenSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='user.id')
    auth_token = serializers.CharField(source='key')

    class Meta:
        model = Token
        fields = ('id', 'auth_token')


class CallbackCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Callback
        fields = '__all__'