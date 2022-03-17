from rest_framework import serializers
from .models import (
    CustomUser,
    Project,

)

class ProjectsSerialiazer(serializers.ModelSerializer):
    creator = serializers.CharField(source='user.username')

    class Meta:
        model = Project
        exclude = ['user',]


class ProjectsCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = '__all__'

class ProjectsDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = '__all__'