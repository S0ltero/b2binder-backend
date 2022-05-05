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

class ChatSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    recepient = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ("pk", "last_message", "recepient")
        depth = 1
        read_only_fields = ("last_message", "recepient")

    def get_last_message(self, obj: Chat):
        return MessageSerializer(obj.messages.order_by("timestamp").last()).data

    def get_recepient(self, obj: Chat):
        recepient = obj.members.exclude(pk=self.context["scope"]["user"].id).first()
        serializer = UserSerializer(recepient)
        return serializer.data


class ChatDetailSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    messages = MessageSerializer(many=True, read_only=True)
    recepient = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ("pk", "messages", "last_message", "recepient")
        depth = 1
        read_only_fields = ("messages", "last_message", "recepient")

    def get_last_message(self, obj: Chat):
        return MessageSerializer(obj.messages.order_by("timestamp").last()).data

    def get_recepient(self, obj: Chat):
        print(self.context)
        recepient = obj.members.exclude(pk=self.context["scope"]["user"].id).first()
        serializer = UserSerializer(recepient)
        return serializer.data