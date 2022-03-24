from rest_framework import serializers
from rest_framework.authtoken.models import Token
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from .models import (
    CustomUser,
    Project,
    Callback,
    UserLike,
    ProjectLike
)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        exclude = ('password', 'last_login', 'groups',
                    'is_superuser', 'is_active', 'is_staff', 'date_joined')


class UserCreateSerializer(DjoserUserCreateSerializer):

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password',
                  'photo', 'profile_type', 'city')

class UserLikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserLike
        fields = ['like_to', 'like_from']

    def to_representation(self, instance):
        self.fields['like_to'] = UserSerializer(read_only=True)
        self.fields['like_from'] = UserSerializer(read_only=True)
        return super().to_representation(instance)



class ProjectLikeSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(slug_field='title', read_only=True)
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = ProjectLike
        fields = ['user', 'project']


class ProjectsSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(slug_field='name', many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id','title', 'short_description', 'categories',
                  'profit', 'investments']


class ProjectsCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        exclude = ('user',)


class ProjectsDetailSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(slug_field='name', many=True, read_only=True)

    class Meta:
        model = Project
        fields = '__all__'


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