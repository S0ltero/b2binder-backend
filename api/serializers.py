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
    ProjectNew
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


class ProjectsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ('id','title', 'short_description', 'categories',
                  'profit', 'investments')

    def to_representation(self, instance):
        self.fields['categories'] = CategorySerializer(many=True, read_only=True)
        return super().to_representation(instance)


class ProjectsCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        exclude = ('user',)

    def to_representation(self, instance):
        self.fields['categories'] = CategorySerializer(many=True, read_only=True)
        return super().to_representation(instance)


class ProjectsDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['categories'] = CategorySerializer(many=True, read_only=True)
        return super().to_representation(instance)


class UserLikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserLike
        fields = ('like_to', 'like_from')

    def to_representation(self, instance):
        self.fields['like_to'] = UserSerializer(read_only=True)
        self.fields['like_from'] = UserSerializer(read_only=True)
        return super().to_representation(instance)


class ProjectLikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectLike
        fields = ('user', 'project')

    def to_representation(self, instance):
        self.fields['project'] = ProjectsSerializer(read_only=True)
        self.fields['user'] = UserSerializer(read_only=True)
        return super().to_representation(instance)


class ProjectCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectComment
        fields = ('user', 'project', 'text')

    def to_representation(self, instance):
        self.fields['user'] = UserSerializer(read_only=True)
        self.fields['project'] = ProjectsSerializer(read_only=True)
        return super().to_representation(instance)


class ProjectNewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectNew
        fields = ('user', 'project', 'text')

    def to_representation(self, instance):
        self.fields['user'] = UserSerializer(read_only=True)
        self.fields['project'] = ProjectsSerializer(read_only=True)
        return super().to_representation(instance)


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