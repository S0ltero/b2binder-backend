from rest_framework import serializers

from api.serializers import UserSerializer

from .models import Chat, Message


class MessageSerializer(serializers.ModelSerializer):
    created_at_formatted = serializers.SerializerMethodField()
    author = UserSerializer()

    class Meta:
        model = Message
        fields = "__all__"
        depth = 1

    def get_created_at_formatted(self, obj:Message):
        return obj.timestamp.strftime("%d-%m-%Y %H:%M:%S")
