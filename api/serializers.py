from rest_framework import serializers
from rest_framework.authtoken.models import Token
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from .models import (
    CustomUser,
    Project,

)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        exclude = ('password', 'last_login', 'groups',
                   'user_permission', 'is_superuser',
                   'is_active', 'is_staff', 'date_joined')


class UserCreateSerializer(DjoserUserCreateSerializer):

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 're_password',
                  'photo', 'profile_type', 'city')



class ProjectsSerialiazer(serializers.ModelSerializer):
    creator = serializers.CharField(source='user.username')

    class Meta:
        model = Project
        exclude = ('user')


class ProjectsCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = '__all__'

class ProjectsDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = '__all__'


class TokenSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='user.id')
    auth_token = serializers.CharField(source='key')

    class Meta:
        model = Token
        fields = ('id', 'auth_token')
