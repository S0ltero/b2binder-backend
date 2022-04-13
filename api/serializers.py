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

    class Meta:
        model = CustomUser
        exclude = ('password', 'last_login', 'groups', 'user_permissions',
                    'is_superuser', 'is_active', 'is_staff', 'date_joined')


class UserCreateSerializer(DjoserUserCreateSerializer):

    class Meta:
        model = CustomUser
        fields = ('email', 'password')


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

    class Meta:
        model = Project
        fields = ('id','title', 'short_description', 'categories',
                  'profit', 'investments')


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